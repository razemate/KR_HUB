from google import genai
from google.genai import types
from openai import OpenAI
from backend.config import GEMINI_API_KEY, OPENROUTER_API_KEY
from core.supabase_client import supabase
from datetime import datetime
import io

def get_user_key(user_id: str, provider: str):
    if not supabase:
        return None
    try:
        response = supabase.table("user_api_keys").select("encrypted_key").eq("user_id", user_id).eq("provider", provider).execute()
        if response.data:
            return response.data[0]["encrypted_key"] 
    except Exception as e:
        print(f"Error fetching user key: {e}")
        pass
    return None

def _run_openrouter(api_key: str, messages: list, model: str = "openrouter/free", temperature: float = 0.7, stream: bool = False):
    """Internal helper to run OpenRouter"""
    client = OpenAI(
        api_key=api_key, 
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Check if model supports reasoning (some free models might)
    extra_body = {}
    if "free" in model or "reasoning" in model:
        extra_body = {"reasoning": {"enabled": True}}

    # Add Default System Instruction if not present
    has_system = any(m['role'] == 'system' for m in messages)
    if not has_system:
         messages.insert(0, {"role": "system", "content": f"You are a professional AI assistant. Today is {datetime.now().strftime('%Y-%m-%d %H:%M')}. Answer concisely and use Markdown for formatting. Do NOT ask for clarification on typos or vague queries; infer the user's intent and provide the best possible answer immediately."})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        extra_body=extra_body,
        stream=stream
    )
    
    if stream:
        return response # Return the generator
    
    return response.choices[0].message.content

def run_ai(user_id: str, messages: list, provider: str = "gemini", model: str = None, temperature: float = 0.7, stream: bool = False, image_data=None):
    """
    Central AI execution function with Fallback Logic.
    Primary: Gemini -> Fallback: OpenRouter (Free)
    """
    
    # 1. Try Primary Provider (Gemini Default)
    try:
        if provider == "gemini":
            # BYOK Check for Gemini
            api_key = get_user_key(user_id, "gemini") or GEMINI_API_KEY
            if not api_key:
                # Check for OpenRouter fallback explicitly before failing
                if OPENROUTER_API_KEY:
                     # Switch provider if Gemini missing but OpenRouter present (implicit fallback)
                     # But logic below handles explicit provider switch.
                     # Here we just raise to trigger the except block which does fallback.
                     raise Exception("Missing Gemini Key")
                else:
                     raise RuntimeError("No AI API key configured. Check config.py or Vercel env variables.")

            api_key = api_key.strip().split()[0]

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            system_instruction = f"You are the Central AI Hub Assistant. Today is {current_time}. Your goal is to be helpful, professional, and concise. When analyzing data, provide clear summaries and use Markdown tables. Always format lists properly. Do NOT ask for clarification on typos or vague queries; infer the user's intent and provide the best possible answer immediately."

            model_name = model or "gemini-flash-latest"

            text_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            contents = [text_prompt]
            if image_data:
                buf = io.BytesIO()
                image_data.save(buf, format="PNG")
                contents.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"))

            if stream:
                class _TextChunk:
                    def __init__(self, text: str):
                        self.text = text

                def stream_generator():
                    try:
                        client = genai.Client(api_key=api_key)
                        for chunk in client.models.generate_content_stream(
                            model=model_name,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=temperature,
                            ),
                        ):
                            yield chunk
                    except Exception as e:
                        # Catch Resource Exhausted (429) inside stream and trigger Fallback manually
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            print(f"Gemini 429 Hit. Falling back to OpenRouter...")
                            try:
                                fallback_key = OPENROUTER_API_KEY
                                if fallback_key:
                                    # We need to manually invoke the OpenRouter stream here
                                    or_response = _run_openrouter(fallback_key, messages, "openrouter/free", temperature, True)
                                    for chunk in or_response:
                                        if hasattr(chunk, 'choices') and chunk.choices[0].delta.content:
                                            yield _TextChunk(chunk.choices[0].delta.content)
                                    return # End successfully
                            except Exception as fb_e:
                                yield _TextChunk(f"Fallback Failed: {str(fb_e)}")
                                return

                        print(f"STREAM ERROR: {e}")
                        yield _TextChunk(f"AI Error: {str(e)}")

                return stream_generator()
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                ),
            )
            return response.text

        elif provider == "openai" or provider == "openrouter":
             # BYOK Check for OpenRouter/OpenAI
            api_key = get_user_key(user_id, "openrouter") or OPENROUTER_API_KEY
            if not api_key: raise Exception("Missing OpenRouter Key")
            api_key = api_key.strip().split()[0]
            
            # Note: For simplicity, we are skipping Image support for OpenRouter fallback in this iteration
            # as it requires base64 encoding and model compatibility checks.
            # If image_data is present, we might warn or just send text.
            
            if api_key.startswith("sk-or"):
                return _run_openrouter(api_key, messages, model or "openrouter/free", temperature, stream)
            else:
                # Standard OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model or "gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature,
                    stream=stream
                )
                
                if stream:
                    return response
                
                return response.choices[0].message.content

    except Exception as e:
        print(f"Primary Provider ({provider}) Failed: {e}. Attempting Fallback to OpenRouter Free...")
        
        # 2. Fallback to OpenRouter Free
        try:
            fallback_key = OPENROUTER_API_KEY
            if fallback_key:
                fallback_key = fallback_key.strip().split()[0]
            if fallback_key and fallback_key.startswith("sk-or"):
                return _run_openrouter(fallback_key, messages, "openrouter/free", temperature, stream)
            else:
                return "AI is temporarily unavailable. Please verify server configuration and try again."
        except Exception as fallback_error:
            return "AI is temporarily unavailable. Please verify server configuration and try again."
