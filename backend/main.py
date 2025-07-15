import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
import shutil
import uuid
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import requests
import psycopg2
import json as pyjson
import re
 
load_dotenv()
 
TEMP_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'temp_upload')
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
 
app = FastAPI(lifespan=None)
 
# Serve static files (frontend)
# app.mount("/", StaticFiles(directory="./frontend", html=True), name="static")
app.mount("/static", StaticFiles(directory="./frontend", html=True), name="static")
 
@app.get("/api/health")
def health_check():
    return {"status": "ok"}
 
@app.get("/")
def read_index():
    return FileResponse("./frontend/index.html")
 
@app.post("/api/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    # Validate file type and size
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    if file.size is not None and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
    # Save file to temp_upload
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(TEMP_UPLOAD_DIR, f"{file_id}.pdf")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Extract text from PDF
    try:
        text = ""
        with open(temp_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        # If text extraction is poor, use OCR
        if len(text.strip()) < 100:
            images = convert_from_path(temp_path)
            for img in images:
                text += pytesseract.image_to_string(img)
        print(text)
    except Exception as e:
        return {"success": False, "error": f"PDF extraction failed: {str(e)}"}
    # Call Gemini LLM to structure data
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        print("Gemini API key:", gemini_api_key)
        prompt = f"""
Extract the following fields from the provided salary slip or Form 16 text. Return a JSON object with these keys: gross_salary, basic_salary, hra_received, rent_paid, deduction_80c, deduction_80d, standard_deduction, professional_tax, tds. If a field is not found, set it to null. Here is the text:\n{text}
"""
        print("helloooooooooo1")
        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=30
            )
            print("helloooooooooo2")
        except Exception as e:
            print("Exception during Gemini API call:", e)
            return {"success": False, "error": f"Gemini API call failed: {str(e)}"}
        if response.status_code != 200:
            return {"success": False, "error": response.text}
        gemini_data = response.json()
        print(gemini_data)
        # Parse Gemini response (assume JSON in first candidate)
        candidates = gemini_data.get("candidates", [])
        if not candidates:
            return {"success": False, "error": "No extraction result from Gemini."}
        content = candidates[0]["content"]["parts"][0]["text"]
        # Remove code block markers and any leading 'json' or whitespace before the JSON object
        content_clean = re.sub(r"^```json\s*|^json\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
        # Now, find the first '{' and slice from there
        json_start = content_clean.find('{')
        if json_start != -1:
            content_clean = content_clean[json_start:]
        try:
            print("content_clean", content_clean)
            fields = pyjson.loads(content_clean)
            print("fields", fields )
        except Exception:
            fields = {k: None for k in ["gross_salary", "basic_salary", "hra_received", "rent_paid", "deduction_80c", "deduction_80d", "standard_deduction", "professional_tax", "tds"]}
        return {"success": True, "fields": fields}
    except Exception as e:
        return {"success": False, "error": f"Gemini extraction failed: {str(e)}"}
 
 
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS userfinancials (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gross_salary NUMERIC(15, 2),
    basic_salary NUMERIC(15, 2),
    hra_received NUMERIC(15, 2),
    rent_paid NUMERIC(15, 2),
    deduction_80c NUMERIC(15, 2),
    deduction_80d NUMERIC(15, 2),
    standard_deduction NUMERIC(15, 2),
    professional_tax NUMERIC(15, 2),
    tds NUMERIC(15, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""
 
# Add table creation for UserAdvisor
CREATE_ADVISOR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS UserAdvisor (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES UserFinancials(session_id),
    question TEXT,
    user_answer TEXT,
    suggestions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

@app.on_event("startup")
def startup_event():
    # Use SUPABASE_DB_URL, SUPABASE_DB_USER, etc. for DB connection
    db_host = os.getenv("SUPABASE_DB_URL")
    db_user = os.getenv("SUPABASE_DB_USER")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_name = os.getenv("SUPABASE_DB_NAME")
    db_port = int(os.getenv("SUPABASE_DB_PORT", 5432))
    try:
        print("[DEBUG] Connecting to DB for table creation...")
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        cur.close()
        conn.close()
        print("[DEBUG] userfinancials table ensured.")
    except Exception as e:
        print(f"[ERROR] Error creating userfinancials table: {e}")

    try:
        print("[DEBUG] Ensuring UserAdvisor table exists...")
        db_host = os.getenv("SUPABASE_DB_URL")
        db_user = os.getenv("SUPABASE_DB_USER")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        db_name = os.getenv("SUPABASE_DB_NAME")
        db_port = int(os.getenv("SUPABASE_DB_PORT", 5432))
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(CREATE_ADVISOR_TABLE_SQL)
        conn.commit()
        cur.close()
        conn.close()
        print("[DEBUG] UserAdvisor table ensured.")
    except Exception as e:
        print(f"[ERROR] Error creating UserAdvisor table: {e}")

@app.post("/api/calculate-tax")
def calculate_tax(
    session_id: str = Form(...),
    gross_salary: float = Form(...),
    basic_salary: float = Form(...),
    hra_received: float = Form(...),
    rent_paid: float = Form(...),
    deduction_80c: float = Form(...),
    deduction_80d: float = Form(...),
    standard_deduction: float = Form(...),
    professional_tax: float = Form(...),
    tds: float = Form(...),
    regime: str = Form(...)
):
    # --- Tax Calculation Logic ---
    def calc_old_regime():
        # Deductions: Standard Deduction, HRA, Professional Tax, 80C, 80D
        deductions = (
            standard_deduction +
            min(hra_received, rent_paid) +
            professional_tax +
            deduction_80c +
            deduction_80d
        )
        taxable_income = max(gross_salary - deductions, 0)
        tax = 0
        slabs = [
            (250000, 0.0),
            (250000, 0.05),
            (500000, 0.20),
            (float('inf'), 0.30)
        ]
        remaining = taxable_income
        for slab_amt, rate in slabs:
            if remaining <= 0:
                break
            amt = min(remaining, slab_amt)
            tax += amt * rate
            remaining -= amt
        cess = 0.04 * tax
        total = tax + cess
        return {
            "taxable_income": round(taxable_income, 2),
            "tax": round(tax, 2),
            "cess": round(cess, 2),
            "total_liability": round(total, 2),
            "breakdown": {
                "gross_salary": gross_salary,
                "deductions": round(deductions, 2),
                "standard_deduction": standard_deduction,
                "hra_received": hra_received,
                "rent_paid": rent_paid,
                "professional_tax": professional_tax,
                "deduction_80c": deduction_80c,
                "deduction_80d": deduction_80d
            }
        }
    def calc_new_regime():
        # Deductions: Only Standard Deduction
        deductions = standard_deduction
        taxable_income = max(gross_salary - deductions, 0)
        tax = 0
        slabs = [
            (300000, 0.0),
            (300000, 0.05),
            (300000, 0.10),
            (300000, 0.15),
            (300000, 0.20),
            (float('inf'), 0.30)
        ]
        remaining = taxable_income
        for slab_amt, rate in slabs:
            if remaining <= 0:
                break
            amt = min(remaining, slab_amt)
            tax += amt * rate
            remaining -= amt
        cess = 0.04 * tax
        total = tax + cess
        return {
            "taxable_income": round(taxable_income, 2),
            "tax": round(tax, 2),
            "cess": round(cess, 2),
            "total_liability": round(total, 2),
            "breakdown": {
                "gross_salary": gross_salary,
                "deductions": round(deductions, 2),
                "standard_deduction": standard_deduction
            }
        }
    old_result = calc_old_regime()
    new_result = calc_new_regime()
    # Save to DB (update userfinancials with calculation results)
    try:
        db_host = os.getenv("SUPABASE_DB_URL")
        db_user = os.getenv("SUPABASE_DB_USER")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        db_name = os.getenv("SUPABASE_DB_NAME")
        db_port = int(os.getenv("SUPABASE_DB_PORT", 5432))
        print("[DEBUG] Connecting to DB for UPSERT...")
        print(f"[DEBUG] DB Host: {db_host}, DB Name: {db_name}, DB User: {db_user}, DB Port: {db_port}")
        print(f"[DEBUG] UPSERT values: session_id={session_id}, gross_salary={gross_salary}, basic_salary={basic_salary}, hra_received={hra_received}, rent_paid={rent_paid}, deduction_80c={deduction_80c}, deduction_80d={deduction_80d}, standard_deduction={standard_deduction}, professional_tax={professional_tax}, tds={tds}")
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO "userfinancials" (
                session_id, gross_salary, basic_salary, hra_received, rent_paid, deduction_80c, deduction_80d, standard_deduction, professional_tax, tds
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (session_id) DO UPDATE SET
                gross_salary=EXCLUDED.gross_salary,
                basic_salary=EXCLUDED.basic_salary,
                hra_received=EXCLUDED.hra_received,
                rent_paid=EXCLUDED.rent_paid,
                deduction_80c=EXCLUDED.deduction_80c,
                deduction_80d=EXCLUDED.deduction_80d,
                standard_deduction=EXCLUDED.standard_deduction,
                professional_tax=EXCLUDED.professional_tax,
                tds=EXCLUDED.tds
            ''',
            (session_id, gross_salary, basic_salary, hra_received, rent_paid, deduction_80c, deduction_80d, standard_deduction, professional_tax, tds)
        )
        conn.commit()
        print("[DEBUG] UPSERT committed successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print("[ERROR] Could not save calculation to DB:", e)
    return {
        "old_regime": old_result,
        "new_regime": new_result,
        "selected_regime": regime
    }

@app.get("/api/debug-all-userfinancials")
def debug_all_userfinancials():
    try:
        db_host = os.getenv("SUPABASE_DB_URL")
        db_user = os.getenv("SUPABASE_DB_USER")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        db_name = os.getenv("SUPABASE_DB_NAME")
        db_port = int(os.getenv("SUPABASE_DB_PORT", 5432))
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute('SELECT * FROM "userfinancials" ORDER BY created_at DESC')
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return JSONResponse(content={"rows": data})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/chat")
async def chat_advisor(request: Request):
    data = await request.form()
    session_id = data.get("session_id")
    user_answer = data.get("user_answer", "")
    # Fetch user financials
    try:
        db_host = os.getenv("SUPABASE_DB_URL")
        db_user = os.getenv("SUPABASE_DB_USER")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        db_name = os.getenv("SUPABASE_DB_NAME")
        db_port = int(os.getenv("SUPABASE_DB_PORT", 5432))
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute('SELECT * FROM "userfinancials" WHERE session_id=%s', (session_id,))
        row = cur.fetchone()
        columns = [desc[0] for desc in cur.description]
        user_data = dict(zip(columns, row)) if row else {}
        cur.close()
        conn.close()
    except Exception as e:
        return {"success": False, "error": f"Could not fetch user data: {e}"}
    # Compose prompt for Gemini
    prompt = f"""
User's tax data: {user_data}\nUser's answer: {user_answer}\n
1. Ask a smart, contextual follow-up question if not already asked.\n2. Provide personalized, actionable investment and tax-saving suggestions for the user.\nReturn a JSON object with 'followup_question' and 'suggestions' (as a list of cards or bullet points).\n"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    suggestions = []
    followup_question = ""
    # Call Gemini or mock
    if gemini_api_key:
        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=30
            )
            gemini_data = response.json()
            candidates = gemini_data.get("candidates", [])
            if candidates:
                content = candidates[0]["content"]["parts"][0]["text"]
                # Try to parse JSON from Gemini
                content_clean = re.sub(r"^```json\s*|^json\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
                json_start = content_clean.find('{')
                if json_start != -1:
                    content_clean = content_clean[json_start:]
                try:
                    parsed = pyjson.loads(content_clean)
                    followup_question = parsed.get("followup_question", "What is your main financial goal this year?")
                    suggestions = parsed.get("suggestions", ["Consider investing in ELSS for 80C benefits.", "Review your HRA eligibility."])
                except Exception:
                    followup_question = "What is your main financial goal this year?"
                    suggestions = ["Consider investing in ELSS for 80C benefits.", "Review your HRA eligibility."]
        except Exception as e:
            followup_question = "What is your main financial goal this year?"
            suggestions = [f"[Gemini API error: {e}]", "Consider investing in ELSS for 80C benefits."]
    else:
        # Mocked response
        followup_question = "What is your main financial goal this year?"
        suggestions = [
            "Consider investing in ELSS for 80C benefits.",
            "Review your HRA eligibility.",
            "Maximize your 80D medical insurance deduction.",
            "Explore NPS for additional tax savings."
        ]
    # Store Q&A and suggestions
    try:
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO "UserAdvisor" (session_id, question, user_answer, suggestions) VALUES (%s, %s, %s, %s)''',
            (session_id, followup_question, user_answer, pyjson.dumps(suggestions))
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return {"success": False, "error": f"Could not save advisor data: {e}"}
    return {
        "success": True,
        "followup_question": followup_question,
        "suggestions": suggestions
    }