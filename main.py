import requests
import hashlib
import time
import os

# ==========================================
# KONFIGURASI AGENT & WALLET
# ==========================================
AGENT_NAME = "variz"
WALLET_ADDRESS = "0xe8b85a40c81545fdc607f3ee5efe53fd0ab3dc34"

# ==========================================
# KONFIGURASI API (Ubah sesuai endpoint aslimu)
# ==========================================
# Ganti dengan URL endpoint untuk mengambil dan mengirim puzzle
API_URL_GET_PUZZLE = os.getenv("API_URL_GET_PUZZLE", "https://bqrapnlqqtjedjyhlfci.supabase.co/rest/v1/puzzles") 
API_URL_SUBMIT_PUZZLE = os.getenv("API_URL_SUBMIT_PUZZLE", "https://bqrapnlqqtjedjyhlfci.supabase.co/rest/v1/submit")

# Ganti dengan API Key/Bearer Token kamu jika ada
API_HEADERS = {
    "Authorization": f"Bearer {os.getenv('SUPABASE_KEY', 'TOKEN_KAMU_DI_SINI')}",
    "Content-Type": "application/json"
}

# ==========================================
# LOGIKA PENYELESAIAN PUZZLE
# ==========================================
def solve_puzzle(prompt_text):
    """Fungsi untuk membaca teks puzzle dan memberikan jawaban otomatis."""
    prompt_text = prompt_text.lower()
    
    # Menjawab puzzle: "SHA-256 hash of the empty string starts with which 6 hex characters?"
    if "sha-256" in prompt_text and "empty string" in prompt_text and "6 hex" in prompt_text:
        # Menghitung hash dari string kosong
        hash_result = hashlib.sha256(b"").hexdigest()
        answer = hash_result[:6] # Hasilnya: e3b0c4
        return answer
        
    # Kamu bisa menambahkan logika elif di sini jika ada puzzle jenis baru
    # elif "pertanyaan_baru" in prompt_text:
    #     return "jawaban_baru"
    
    return "unknown"

# ==========================================
# MINING LOOP
# ==========================================
def run_miner():
    print(f"🚀 Memulai Miner Agent '{AGENT_NAME}' untuk wallet {WALLET_ADDRESS}...")
    
    while True:
        try:
            # 1. MENGAMBIL PUZZLE (Timeout diset 60 detik agar tidak RTO)
            response = requests.get(API_URL_GET_PUZZLE, headers=API_HEADERS, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Sesuaikan cara mengambil ID dan prompt dari format JSON aslimu
                puzzle_id = data.get("id")
                prompt = data.get("prompt", "")
                
                if puzzle_id and prompt:
                    print(f"\n[puzzle] id={puzzle_id} prompt='{prompt}'")
                    
                    # 2. MENYELESAIKAN PUZZLE
                    answer = solve_puzzle(prompt)
                    
                    # 3. MENGIRIM JAWABAN
                    submit_payload = {
                        "agent": AGENT_NAME,
                        "wallet": WALLET_ADDRESS,
                        "id": puzzle_id, 
                        "answer": answer
                    }
                    
                    submit_response = requests.post(API_URL_SUBMIT_PUZZLE, json=submit_payload, headers=API_HEADERS, timeout=60)
                    print(f"[submit] attempt=1 status={submit_response.status_code} body={submit_response.text}")
                else:
                    print("[info] Tidak ada puzzle aktif saat ini.")
            else:
                print(f"[error] Gagal mengambil puzzle. Status: {response.status_code}")
                
            # Jeda agar tidak terkena rate limit dari server
            time.sleep(20)
            
        except requests.exceptions.ReadTimeout:
            # Penanganan khusus jika server supabase lambat merespons
            print(f"[error] Network error: HTTPSConnectionPool Read timed out. Mencoba lagi...")
            time.sleep(5)
            
        except requests.exceptions.RequestException as e:
            # Penanganan error jaringan lainnya
            print(f"[error] Network error: {e}")
            time.sleep(5)
            
        except Exception as e:
            print(f"[error] Terjadi kesalahan sistem: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_miner()
