import requests
import hashlib
import time
import re
import os
import sys

# Tambahkan pengecekan library di awal agar tidak "stuck"
try:
    from groq import Groq
except ImportError:
    print("[CRITICAL ERROR] Library 'groq' tidak ditemukan! Pastikan requirements.txt sudah benar.")
    sys.exit(1)

# ==========================================
# KONFIGURASI AGENT
# ==========================================
AGENT_NAME = "variz"
WALLET_ADDRESS = "0xe8b85a40c81545fdc607f3ee5efe53fd0ab3dc34"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxcmFwbmxxcXRqZWRqeWhsZmNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNzUyNjQsImV4cCI6MjA5Mzg1MTI2NH0.mf0fz6kAnK0yeAXrb-XT6yikbdRmeAq5jsikVPPhaFE"

URL_GET_PUZZLE = f"https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1/submit-solution?eth={WALLET_ADDRESS}"
URL_SUBMIT_SOLUTION = "https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1/submit-solution"

# Pengecekan API Key Groq di awal
GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    print("[CRITICAL ERROR] GROQ_API_KEY tidak ditemukan di Variables Railway!")
    # Jangan sys.exit supaya container tidak restart terus-menerus (loop)
    while True: time.sleep(100) 

client = Groq(api_key=GROQ_KEY)
attempt_counter = 0 

def solve_puzzle(prompt_text):
    global attempt_counter
    p_lower = prompt_text.lower()
    
    # Jawaban pasti dari soul.md & diskusi kita
    if "soul.md" in p_lower: return "eth"
    if "nk stand for" in p_lower: return "north korea"
    if "bitcoin whitepaper" in p_lower: return "2008"
    if "chain id is base mainnet" in p_lower: return "8453"
    if "hex value of decimal 255" in p_lower: return "ff"
    
    # Kalkulator
    if "reverse the bits" in p_lower:
        m = re.search(r'0b([01]+)', p_lower)
        if m: return f"{int(m.group(1).zfill(8)[::-1], 2):02x}"
    
    # AI Fallback
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": "Direct answer only."}, {"role": "user", "content": prompt_text}],
            model="llama-3.3-70b-versatile"
        )
        return resp.choices[0].message.content.strip()
    except: return "unknown"

def run_miner():
    print(f"🚀 Agent '{AGENT_NAME}' sedang mencoba terhubung...")
    while True:
        try:
            # Tambahkan Timeout agar tidak stuck selamanya jika server down
            get_resp = requests.get(URL_GET_PUZZLE, headers={"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}"}, timeout=15)
            
            if get_resp.status_code == 200:
                data = get_resp.json()
                puzzle = data.get("puzzle")
                
                if not puzzle:
                    print(f"😴 [19:40] Semua puzzle sudah beres. Tidur 60 detik...")
                    time.sleep(60)
                    continue
                
                print(f"💡 Dapat soal: {puzzle.get('prompt')[:50]}...")
                ans = solve_puzzle(puzzle.get('prompt'))
                
                payload = {"eth_address": WALLET_ADDRESS, "agent_name": AGENT_NAME, "puzzle_id": puzzle.get('id'), "answer": ans.lower()}
                post = requests.post(URL_SUBMIT_SOLUTION, json=payload, headers={"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}"}, timeout=15)
                print(f"✅ Submit Result: {post.text}")
            else:
                print(f"❌ Server Error: {get_resp.status_code}. Mencoba lagi...")
            
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Koneksi tersendat: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_miner()
