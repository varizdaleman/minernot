import requests
import hashlib
import time
import re
import os
from google import genai # <-- Menggunakan library baru
from google.genai import types

# ==========================================
# KONFIGURASI SESUAI soul.md & AI
# ==========================================
AGENT_NAME = "variz"
WALLET_ADDRESS = "0xe8b85a40c81545fdc607f3ee5efe53fd0ab3dc34"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxcmFwbmxxcXRqZWRqeWhsZmNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNzUyNjQsImV4cCI6MjA5Mzg1MTI2NH0.mf0fz6kAnK0yeAXrb-XT6yikbdRmeAq5jsikVPPhaFE"

URL_GET_PUZZLE = f"https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1/submit-solution?eth={WALLET_ADDRESS}"
URL_SUBMIT_SOLUTION = "https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1/submit-solution"

API_HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- KONFIGURASI OTAK AI BARU ---
# Pastikan GEMINI_API_KEY sudah terpasang di Variables Railway
client = genai.Client() # Library baru otomatis mencari GEMINI_API_KEY di environment

# ==========================================
# LOGIKA PENYELESAIAN PUZZLE (HYBRID)
# ==========================================
def solve_puzzle(prompt_text):
    prompt_lower = prompt_text.lower()

    # 1. HARDCODE: Untuk kriptografi murni
    if "sha-256 hash of the empty string" in prompt_lower and "6 hex" in prompt_lower:
        hash_result = hashlib.sha256(b"").hexdigest()
        return hash_result[:6]
        
    elif "post-quantum signature" in prompt_lower and "nist in 2024" in prompt_lower:
        return "ml-dsa"

    # 2. AUTO AI: Jika bot tidak tahu, lempar ke AI!
    else:
        print(f"[bot] Berpikir menggunakan AI untuk pertanyaan ini...")
        try:
            ai_prompt = f"""
            You are a competitive puzzle solver. Read the following puzzle/trivia question and provide ONLY the direct answer.
            Do not include any punctuation, explanation, or conversational text. 
            If the answer is a year, output just the number.
            
            Question: "{prompt_text}"
            Answer:
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            ai_answer = response.text.strip()
            return ai_answer
            
        except Exception as e:
            print(f"[error] Otak AI gagal merespons: {e}")
            return "unknown_answer"

def normalize_answer(answer):
    answer = answer.lower().strip()
    answer = re.sub(r'\s+', ' ', answer)
    return answer

# ==========================================
# MINING LOOP OTONOM
# ==========================================
def run_miner():
    print(f"🚀 Memulai Agent '{AGENT_NAME}' dengan AI Brain (GenAI terbaru)...")
    
    while True:
        try:
            get_resp = requests.get(URL_GET_PUZZLE, headers=API_HEADERS, timeout=60)
            
            if get_resp.status_code == 429:
                print("[warning] Rate limit. Jeda 15 detik...")
                time.sleep(15)
                continue
                
            if get_resp.status_code != 200:
                print(f"[error] Gagal PULL puzzle. HTTP Status: {get_resp.status_code}")
                time.sleep(5)
                continue

            data = get_resp.json()
            puzzle = data.get("puzzle")
            
            if not puzzle:
                print("[info] Puzzle pool exhausted. Idle for 60 seconds...")
                time.sleep(60)
                continue
                
            p_id = puzzle.get("id")
            p_prompt = puzzle.get("prompt")
            print(f"\n[puzzle] id={p_id} prompt='{p_prompt}'")
            
            raw_answer = solve_puzzle(p_prompt)
            final_answer = normalize_answer(raw_answer)
            print(f"[solve] Jawaban ditemukan: '{final_answer}'")
            
            payload = {
                "eth_address": WALLET_ADDRESS,
                "agent_name": AGENT_NAME,
                "puzzle_id": p_id,
                "answer": final_answer
            }
            
            post_resp = requests.post(URL_SUBMIT_SOLUTION, json=payload, headers=API_HEADERS, timeout=60)
            
            if post_resp.status_code == 429:
                print("[warning] Rate limit saat SUBMIT. Jeda 15 detik...")
                time.sleep(15)
                continue
                
            print(f"[submit] status={post_resp.status_code} body={post_resp.text}")
            time.sleep(3)
            
        except Exception as e:
            print(f"[error] Terjadi kesalahan: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_miner()
