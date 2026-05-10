import requests
import hashlib
import time
import re

# ==========================================
# KONFIGURASI SESUAI soul.md
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

# ==========================================
# LOGIKA PENYELESAIAN PUZZLE
# ==========================================
def solve_puzzle(prompt_text):
    prompt_lower = prompt_text.lower()
    
    # 1. Puzzle: SHA-256 empty string (seperti di log kamu sebelumnya)
    if "sha-256 hash of the empty string" in prompt_lower and "6 hex" in prompt_lower:
        hash_result = hashlib.sha256(b"").hexdigest()
        return hash_result[:6] 
        
    # [!] KAMU BISA TAMBAHKAN LOGIKA UNTUK PUZZLE LAINNYA DI SINI NANTI
    
    return "unknown_answer"

def normalize_answer(answer):
    """Aturan dari soul.md: lowercase, trimmed, single-spaced"""
    # Mengubah ke huruf kecil, menghapus spasi awal/akhir, mengubah spasi ganda jadi tunggal
    answer = answer.lower().strip()
    answer = re.sub(r'\s+', ' ', answer)
    return answer

# ==========================================
# MINING LOOP OTONOM
# ==========================================
def run_miner():
    print(f"🚀 Memulai Agent '{AGENT_NAME}' untuk wallet {WALLET_ADDRESS}...")
    print("Mempersiapkan quantum mining resistance...\n")
    
    while True:
        try:
            # --- TAHAP 1: PULL PUZZLE ---
            get_resp = requests.get(URL_GET_PUZZLE, headers=API_HEADERS, timeout=60)
            
            # Cek Rate Limit (Golden Rule 5)
            if get_resp.status_code == 429:
                print("[warning] Rate limit (HTTP 429) tercapai saat PULL. Jeda 15 detik...")
                time.sleep(15)
                continue
                
            if get_resp.status_code != 200:
                print(f"[error] Gagal PULL puzzle. HTTP Status: {get_resp.status_code} | Body: {get_resp.text}")
                time.sleep(5)
                continue

            data = get_resp.json()
            puzzle = data.get("puzzle")
            
            # Jika puzzle pool habis (Golden Rule 4)
            if not puzzle:
                print("[info] Puzzle pool exhausted. Idle for 60 seconds...")
                time.sleep(60)
                continue
                
            p_id = puzzle.get("id")
            p_prompt = puzzle.get("prompt")
            p_reward = puzzle.get("reward", 500)
            print(f"\n[puzzle] id={p_id} reward={p_reward} prompt='{p_prompt}'")
            
            # --- TAHAP 2: SOLVE PUZZLE ---
            raw_answer = solve_puzzle(p_prompt)
            final_answer = normalize_answer(raw_answer)
            print(f"[solve] Mempersiapkan jawaban: '{final_answer}'")
            
            # --- TAHAP 3: SUBMIT SOLUTION ---
            payload = {
                "eth_address": WALLET_ADDRESS,
                "agent_name": AGENT_NAME,
                "puzzle_id": p_id,
                "answer": final_answer
            }
            
            post_resp = requests.post(URL_SUBMIT_SOLUTION, json=payload, headers=API_HEADERS, timeout=60)
            
            # Cek Rate Limit (Golden Rule 5)
            if post_resp.status_code == 429:
                print("[warning] Rate limit (HTTP 429) tercapai saat SUBMIT. Jeda 15 detik...")
                time.sleep(15)
                continue
                
            print(f"[submit] status={post_resp.status_code} body={post_resp.text}")
            
            # Jeda 2-3 detik agar tidak memicu HTTP 429 terlalu cepat (max 8 req/10s)
            time.sleep(3)
            
        except requests.exceptions.ReadTimeout:
            print("[error] Network Timeout. Server terlalu lama merespons. Mencoba lagi...")
            time.sleep(5)
            
        except Exception as e:
            print(f"[error] Terjadi kesalahan tak terduga: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_miner()
