from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.auth_manager import get_current_user
from core.ai_gateway import run_ai
from core.supabase_client import supabase
from pydantic import BaseModel
import json
import pandas as pd
import io
from rapidfuzz import process, fuzz
import PyPDF2
import openpyxl
import docx
import csv
from PIL import Image

router = APIRouter(prefix="/modules/chat-with-data", tags=["chat-with-data"])

@router.post("/analyze")
async def analyze(
    question: str = Form(...),
    table_name: str = Form("profiles"),
    mode: str = Form("database"), # 'general' or 'database'
    file: UploadFile = File(None),
    user=Depends(get_current_user)
):
    user_id = user.id if not isinstance(user, dict) else user.get("id")
    
    file_context = ""
    image_data = None

    if file:
        try:
            content = await file.read()
            filename = file.filename.lower()
            
            # --- Text/Code Files ---
            if filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.sql', '.sh')):
                try:
                    text_content = content.decode('utf-8')
                    file_context = f"Uploaded File Content ({file.filename}):\n{text_content[:10000]}\n"
                except UnicodeDecodeError:
                    file_context = f"Uploaded File ({file.filename}) is binary or not UTF-8 encoded.\n"

            # --- CSV (Lightweight, No Pandas) ---
            elif filename.endswith('.csv'):
                try:
                    text_data = content.decode('utf-8')
                    reader = csv.DictReader(io.StringIO(text_data))
                    rows = list(reader)[:20] # Limit to 20 rows
                    file_context = f"Uploaded CSV Data ({file.filename}):\n{json.dumps(rows, indent=2)}\n"
                except Exception as csv_err:
                    file_context = f"Error reading CSV: {str(csv_err)}\n"
            
            # --- Excel (Lightweight, No Pandas) ---
            elif filename.endswith(('.xlsx', '.xls')):
                try:
                    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
                    ws = wb.active
                    rows = []
                    headers = [cell.value for cell in next(ws.rows)]
                    
                    for row in ws.iter_rows(min_row=2, max_row=21, values_only=True):
                        rows.append(dict(zip(headers, row)))
                        
                    file_context = f"Uploaded Excel Data ({file.filename}):\n{json.dumps(rows, default=str, indent=2)}\n"
                except Exception as xl_err:
                    file_context = f"Error reading Excel: {str(xl_err)}\n"

            # --- Word Document ---
            elif filename.endswith('.docx'):
                try:
                    doc = docx.Document(io.BytesIO(content))
                    text = "\n".join([para.text for para in doc.paragraphs])
                    file_context = f"Uploaded Word Doc Content ({file.filename}):\n{text[:5000]}\n"
                except Exception as doc_err:
                    file_context = f"Error reading Word Doc: {str(doc_err)}\n"

            # --- PDF ---
            elif filename.endswith('.pdf'):
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf_reader.pages[:5]: 
                        text += page.extract_text() + "\n"
                    file_context = f"Uploaded PDF Content ({file.filename}):\n{text[:5000]}\n"
                except Exception as pdf_err:
                    file_context = f"Error reading PDF: {str(pdf_err)}\n"
            
            # --- Images ---
            elif filename.endswith(('.png', '.jpg', '.jpeg', '.webp', '.heic')):
                try:
                    # Open image to verify
                    img = Image.open(io.BytesIO(content))
                    # We pass the PIL Image object to the AI gateway
                    image_data = img
                    file_context = f"Uploaded Image: {file.filename} (Attached for analysis)\n"
                except Exception as img_err:
                    file_context = f"Error reading Image: {str(img_err)}\n"
            
            else:
                file_context = f"Uploaded file type ({file.filename}) is not explicitly supported, but here is the raw info: {file.filename}\n"

        except Exception as e:
            file_context = f"Error reading file: {str(e)}\n"

    # --- GENERAL MODE ---
    if mode == "general":
        # Just run the AI with the file context (if any) and the question
        final_messages = [
            {"role": "user", "content": f"{file_context}\n\nQuestion: {question}"}
        ]
        
        # Enable Streaming
        from fastapi.responses import StreamingResponse
        # Pass image_data if present
        stream_generator = run_ai(user_id, final_messages, temperature=0.7, provider="gemini", stream=True, image_data=image_data)
        
        async def generate_chunks_general():
            try:
                if isinstance(stream_generator, str):
                    yield f"data: {json.dumps({'chunk': stream_generator})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                for chunk in stream_generator:
                    if hasattr(chunk, 'text'):
                        text = chunk.text
                        if text: yield f"data: {json.dumps({'chunk': text})}\n\n"
                    elif hasattr(chunk, 'choices'): 
                        delta = chunk.choices[0].delta.content
                        if delta: yield f"data: {json.dumps({'chunk': delta})}\n\n"
                
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'chunk': f'Error: {str(e)}'})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate_chunks_general(), media_type="text/event-stream")

    # --- DATABASE MODE (Default) ---
    # Step 1: Intelligent Table Selection with Fuzzy Matching
    # Defaults to whatever the frontend sent, but we try to find a better match in the question
    used_table = table_name 
    q_lower = question.lower()
    
    # List of known tables - In a real app, you might fetch this dynamically from information_schema
    possible_tables = ["subscribers", "orders", "products", "woocommerce", "users", "profiles"]
    
    # 1. Check for exact match first
    found_exact = False
    for t in possible_tables:
        if t in q_lower:
            used_table = t
            found_exact = True
            break
            
    # 2. If no exact match, try fuzzy matching against the question words
    if not found_exact:
        # We look for the "best match" table name in the question
        # e.g. "sers" -> "users", "subs" -> "subscribers"
        # We process the whole question against the table list
        best_match = process.extractOne(q_lower, possible_tables, scorer=fuzz.partial_ratio)
        
        # If confidence is high enough (e.g., > 70%), use it
        if best_match and best_match[1] > 70:
             # Verify if the match is actually meaningful (length check or better scoring)
             # Let's try a stricter extraction: extract from words
             words = q_lower.split()
             best_word_match = process.extractOne(used_table, words, scorer=fuzz.ratio)
             
             # If the user typed "sers", fuzz.ratio("sers", "users") is high.
             # We want to find which table name is closest to ANY word in the input.
             
             highest_score = 0
             best_table = used_table
             
             for t in possible_tables:
                 # Check similarity of this table to any word in the question
                 match = process.extractOne(t, words, scorer=fuzz.ratio)
                 if match and match[1] > highest_score:
                     highest_score = match[1]
                     best_table = t
            
             if highest_score > 60: # Threshold for "probably meant this table"
                 used_table = best_table

    # Verify existence of the chosen table (Robust check)
    try:
        supabase.table(used_table).select("*").limit(1).execute()
    except:
        # If the guessed table doesn't exist, fall back to 'profiles' or just proceed and let it fail gracefully
        pass

    # Step 2: AI-Driven Query Generation (Natural Language -> Supabase Filter)
    filter_instruction = ""
    db_context = "[]"
    
    try:
        # Fetch 1 row to get column names for context
        schema_sample = supabase.table(used_table).select("*").limit(1).execute()
        columns = list(schema_sample.data[0].keys()) if schema_sample.data else []
        
        query_builder = supabase.table(used_table).select("*")
        
        # Fuzzy Filter Logic: Check if "active" or similar words are in the query
        # This is a basic example. For true robustness, we'd feed schema to AI and ask for SQL/JSON filter.
        # But here we stick to Python logic for speed.
        
        if "status" in columns:
            # Check for 'active'
            if fuzz.partial_ratio("active", q_lower) > 80:
                 query_builder = query_builder.eq("status", "active")
                 filter_instruction += "(Filtered by status='active')"
        
        # Limit to 50 for context window safety
        data_res = query_builder.limit(50).execute()
        db_context = json.dumps(data_res.data)
        
        if len(data_res.data) == 0:
             db_context = f"No data found in table '{used_table}' {filter_instruction}. The database might be empty or no matching records."
             
    except Exception as e:
        db_context = f"Error fetching data from '{used_table}': {str(e)}"
        
        # Enhanced Error Handling for Schema Cache Issues
        if "PGRST205" in str(e):
            db_context = (
                f"⚠️ **CRITICAL ERROR: Table '{used_table}' exists but is not visible to the API.**\n\n"
                f"**CAUSE:** The Supabase Schema Cache is outdated.\n"
                f"**FIX REQUIRED:**\n"
                f"1. Go to your Supabase Dashboard > Settings > API.\n"
                f"2. Click the **'Reload schema cache'** button.\n"
                f"3. Try this query again.\n\n"
                f"(Original Error: {str(e)})"
            )

    # Construct Prompt
    # We explicitly tell the AI to be permissive and infer intent
    final_messages = [
        {"role": "user", "content": f"""
        CONTEXT:
        - Table: {used_table}
        - Schema Columns: {columns if 'columns' in locals() else 'Unknown'}
        - Database Data Sample: {db_context}
        - File Content: {file_context}
        
        USER QUESTION: "{question}"
        
        INSTRUCTIONS:
        1. The user might have typos (e.g., "sers" instead of "users"). INFER their intent based on the available data.
        2. Do NOT ask for clarification unless absolutely impossible to answer.
        3. If the data provides a clear answer (e.g., a count), state it directly.
        4. If the user asks for "active subscribers" and you see "status: active" in the data, count them and answer.
        5. Be helpful, direct, and smart.
        """}
    ]
    
    # Run AI
    from fastapi.responses import StreamingResponse
    
    # We need to adapt the run_ai to support streaming or wrap it
    # Since run_ai returns text or a generator, we need to handle both.
    # Let's request streaming from run_ai
    
    # Pass image_data here as well
    stream_generator = run_ai(user_id, final_messages, temperature=0.5, provider="gemini", stream=True, image_data=image_data)
    
    async def generate_chunks():
        try:
            # Check if it's a string (error message)
            if isinstance(stream_generator, str):
                yield f"data: {json.dumps({'chunk': stream_generator})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # Gemini Stream
            for chunk in stream_generator:
                if hasattr(chunk, 'text'):
                    text = chunk.text
                    if text:
                        yield f"data: {json.dumps({'chunk': text})}\n\n"
                elif hasattr(chunk, 'choices'): # OpenAI Stream
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield f"data: {json.dumps({'chunk': delta})}\n\n"
                        
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'chunk': f'Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate_chunks(), media_type="text/event-stream")
