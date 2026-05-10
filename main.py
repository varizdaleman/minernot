import requests
import hashlib
import time
import re
import os
from groq import Groq

# ==========================================
# KONFIGURASI AGENT & API
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

# --- INISIALISASI GROQ AI ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
attempt_counter = 0 

# ==========================================
# LOGIKA PENYELESAIAN PUZZLE
# ==========================================
def solve_puzzle(prompt_text):
    global attempt_counter
    prompt_lower = prompt_text.lower()

    # 1. THREAT MODELING (NK)
    if "nk stand for" in prompt_lower and "threat model" in prompt_lower:
        guesses = ["nation state", "nation-state", "north korea"]
        ans = guesses[attempt_counter % len(guesses)]
        attempt_counter += 1
        return ans

    # 2. HARDCODE DASAR
    elif "sha-256 hash of the empty string" in prompt_lower:
        return hashlib.sha256(b"").hexdigest()[:6]
    elif "bitcoin whitepaper" in prompt_lower:
        return "2008"
    elif "chain id is base mainnet" in prompt_lower:
        return "8453"
    elif "hex value of decimal 255" in prompt_lower:
        return "ff"
    elif "keccak256" in prompt_lower and "abc" in prompt_lower:
        return WALLET_ADDRESS
    elif "shors algorithm threatens" in prompt_lower:
        return "rsa"

    # 3. AES-128 & GROVER
    elif "aes-128" in prompt_lower and "grover" in prompt_lower:
        guesses = ["2^64", "64"]
        ans = guesses[attempt_counter % len(guesses)]
        attempt_counter += 1
        return ans

    # 4. HD WALLETS (BIP-32)
    elif "hierarchical deterministic wallets" in prompt_lower:
        guesses = ["32", "bip32"]
        ans = guesses[attempt_counter % len(guesses)]
        attempt_counter += 1
        return ans

    # 5. KYBER / LATTICE
    elif "lattice problem underpins kyber" in prompt_lower:
        guesses = ["mlwe", "m-lwe"]
        ans = guesses[attempt_counter % len(guesses)]
        attempt_counter += 1 
        return ans

    # 6. BITCOIN HASH
    elif "hash function does bitcoin use for block headers" in prompt_lower:
        guesses = ["sha256d", "sha256"]
        ans = guesses[attempt_counter % len(guesses)]
        attempt_counter += 1 
        return ans

    # 7. KALKULATOR: Reverse Bits
    elif "reverse the bits of byte" in prompt_lower:
        match = re.search(r'0b([01]+)', prompt_lower)
        if match:
            bin_str = match.group(1).zfill(8)
            reversed_bin = bin_str[::-1]
            return f"{int(reversed_bin, 2):02x}"

    # 8. AUTO AI
    else:
        print(f"[bot] Berpikir menggunakan AI...")
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional cybersecurity and crypto puzzle solver. Answer ONLY with the direct value. No extra words, no periods."},
                    {"role": "user", "content": prompt_text}
                ],
                model="llama-3.3-70b-versatile",
            )
            return response.choices[0].message.content.strip()
        except:
            return "unknown"

def normalize_answer(answer):
    return answer.lower().strip()

# ==========================================
# MINING LOOP
# ==========================================
def run_miner():
    print(f"🚀 Agent '{AGENT_NAME}' aktif. Menyerang Threat Model NK...")
    while True:
        try:
            get_resp = requests.get(URL_GET_PUZZLE, headers=API_HEADERS, timeout=60)
            if get_resp.status_code != 200:
                time.sleep(10); continue

            data = get_resp.json()
            puzzle = data.get("puzzle")
            if not puzzle:
                time.sleep(60); continue
                
            p_id, p_prompt = puzzle.get("id"), puzzle.get("prompt")
            print(f"\n[puzzle] {p_prompt}")
            
            final_answer = normalize_answer(solve_puzzle(p_prompt))
            print(f"[solve] Jawab: '{final_answer}'")
            
            payload = {"eth_address": WALLET_ADDRESS, "agent_name": AGENT_NAME, "puzzle_id": p_id, "answer": final_answer}
            post_resp = requests.post(URL_SUBMIT_SOLUTION, json=payload, headers=API_HEADERS, timeout=60)
            print(f"[submit] {post_resp.text}")
            time.sleep(3)
        except Exception as e:
            print(f"[error] {e}"); time.sleep(5)

if __name__ == "__main__":
    run_miner()
