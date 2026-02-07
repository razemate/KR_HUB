import google.generativeai as genai
from openai import OpenAI
from core.config_manager import config
from core.supabase_client import supabase
from datetime import datetime

def get_user_key(user_id: str, provider: str):
    # Supabase client is guaranteed to be valid by core.supabase_client
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
            api_key = get_user_key(user_id, "gemini") or config.get("GLOBAL_GEMINI_KEY")
            if not api_key: raise Exception("Missing Gemini Key")

            genai.configure(api_key=api_key)
            # Use 'gemini-1.5-flash' for speed
            model_name = model or "gemini-1.5-flash"
            
            # Enable Google Search Tool (Grounding) if available in this library version
            # Note: Explicit 'tools' config is safer.
            tools = [{"google_search": {}}]
            
            gemini_model = genai.GenerativeModel(model_name, tools=tools)
            
            # Simple conversion for Gemini
            # If image_data is provided (PIL Image), we construct a multi-modal prompt
            
            full_prompt = []
            
            # Add System Instruction (Prepended to prompt for V1 API)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            system_instruction = f"System: You are the Central AI Hub Assistant. Today is {current_time}. Your goal is to be helpful, professional, and concise. When analyzing data, provide clear summaries and use Markdown tables. Always format lists properly. Do NOT ask for clarification on typos or vague queries; infer the user's intent and provide the best possible answer immediately."
            full_prompt.append(system_instruction)
            
            # Add messages
            for m in messages:
                full_prompt.append(f"{m['role']}: {m['content']}")
            
            if image_data:
                # Append image to the end of prompt
                full_prompt.append(image_data)

            if stream:
                return gemini_model.generate_content(full_prompt, stream=True)
            
            response = gemini_model.generate_content(full_prompt)
            return response.text

        elif provider == "openai" or provider == "openrouter":
             # BYOK Check for OpenRouter/OpenAI
            api_key = get_user_key(user_id, "openrouter") or config.get("GLOBAL_OPENAI_KEY")
            if not api_key: raise Exception("Missing OpenRouter Key")
            
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
            fallback_key = config.get("GLOBAL_OPENAI_KEY")
            if fallback_key and fallback_key.startswith("sk-or"):
                return _run_openrouter(fallback_key, messages, "openrouter/free", temperature, stream)
            else:
                return f"AI Error: Primary failed ({e}) and no OpenRouter fallback key available."
        except Exception as fallback_error:
            return f"AI Critical Error: Primary ({e}) and Fallback ({fallback_error}) both failed."
