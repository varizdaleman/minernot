import requests
import time
import hashlib
import base64
import json
import os
import re
from groq import Groq

API_URL = "https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1/submit-solution"

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxcmFwbmxxcXRqZWRqeWhsZmNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNzUyNjQsImV4cCI6MjA5Mzg1MTI2NH0.mf0fz6kAnK0yeAXrb-XT6yikbdRmeAq5jsikVPPhaFE"

# Pastikan ini adalah alamat wallet terbarumu!
WALLET = "0x716019a1ff081a9ddfd568f3e277425e3bbab380"
AGENT = "varizgan"

# =========================
# GROQ AI
# =========================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

# =========================
# HEADERS
# =========================

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

# =========================
# CACHE (MEMORI JAWABAN)
# =========================

CACHE_FILE = "answers.json"

try:
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
except:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

# =========================
# GET PUZZLE
# =========================

def get_puzzle():
    url = f"{API_URL}?eth={WALLET}"
    response = requests.get(
        url,
        headers=headers,
        timeout=30 # Dipercepat agar bot tidak stuck kalau server lag
    )
    return response.json()

# =========================
# LOCAL SOLVERS
# =========================

def solve_sha256_empty():
    result = hashlib.sha256(b"").hexdigest()
    return result[:6]

def solve_base64(prompt):
    try:
        text = prompt.split("'")[1]
        decoded = base64.b64decode(text).decode()
        return decoded.lower().strip()
    except:
        return None

def solve_generic_reverse(prompt):
    try:
        text = prompt.split("'")[1]
        return text[::-1].lower().strip()
    except:
        return None

def solve_math(prompt):
    try:
        expression = (
            prompt.lower()
            .replace("calculate", "")
            .replace("what is", "")
            .replace("=", "")
            .strip()
        )
        result = eval(expression)
        return str(result)
    except:
        return None

# =========================
# GROQ AI
# =========================

def ask_groq(prompt):
    if not groq_client:
        return None

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Model terbaru dan tercerdas
            messages=[
                {
                    "role": "system",
                    "content": "You solve cryptographic and logic puzzles. Return ONLY the direct final answer. No punctuation, no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
        answer = response.choices[0].message.content
        return answer.lower().strip()

    except Exception as e:
        print("[GROQ ERROR]", e)
        return None

# =========================
# MAIN SOLVER
# =========================

def solve_puzzle(puzzle):
    prompt = puzzle["prompt"]
    prompt_lower = prompt.lower()

    print(f"\n[PUZZLE] {prompt}")

    # 1. CEK HARDCODE TERLEBIH DAHULU (Prioritas Tertinggi)
    if "soul.md" in prompt_lower: return "eth"
    if "nk stand for" in prompt_lower: return "north korea"
    if "nist in 2024" in prompt_lower: return "dilithium"
    if "bitcoin whitepaper" in prompt_lower: return "2008"
    if "chain id is base mainnet" in prompt_lower: return "8453"
    if "hex value of decimal 255" in prompt_lower: return "ff"
    if "hierarchical deterministic wallets" in prompt_lower: return "32"
    if "lattice problem underpins kyber" in prompt_lower: return "mlwe"
    if "hash function does bitcoin use for block headers" in prompt_lower: return "sha256d"
    if "aes-128" in prompt_lower and "grover" in prompt_lower: return "2^64"
    if "shors algorithm threatens" in prompt_lower: return "rsa"
    if "keccak256" in prompt_lower and "abc" in prompt_lower: return WALLET
    
    # Kalkulator Biner Spesifik
    if "reverse the bits" in prompt_lower:
        m = re.search(r'0b([01]+)', prompt_lower)
        if m: return f"{int(m.group(1).zfill(8)[::-1], 2):02x}"

    # 2. CEK CACHE
    if prompt in cache:
        print("[CACHE] Using cached answer")
        return cache[prompt]

    answer = None

    # 3. PARSER DINAMIS
    if "sha-256 hash of the empty string" in prompt_lower:
        answer = solve_sha256_empty()
    elif "base64" in prompt_lower:
        answer = solve_base64(prompt)
    elif "reverse" in prompt_lower: # Untuk reverse string biasa
        answer = solve_generic_reverse(prompt)
    elif "calculate" in prompt_lower or "what is" in prompt_lower:
        answer = solve_math(prompt)

    # 4. GROQ AI FALLBACK
    if not answer:
        print("[AI] Using Groq AI...")
        answer = ask_groq(prompt)

    # Simpan ke Cache jika berhasil
    if answer:
        answer = str(answer).lower().strip()
        if answer != "none" and answer != "unknown":
            cache[prompt] = answer
            save_cache()

    return answer

# =========================
# SUBMIT
# =========================

def submit_answer(puzzle_id, answer):
    payload = {
        "eth_address": WALLET,
        "agent_name": AGENT,
        "puzzle_id": puzzle_id,
        "answer": answer
    }
    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    return response.json()

# =========================
# START
# =========================

print(f"[MINER] Started successfully for Agent: {AGENT}")

while True:
    try:
        data = get_puzzle()
        puzzle = data.get("puzzle")

        if not puzzle:
            print("[INFO] No puzzle available. Puzzles might be all solved. Waiting 60s...")
            time.sleep(60)
            continue

        answer = solve_puzzle(puzzle)

        if not answer:
            print("[INFO] Could not solve puzzle")
            time.sleep(10)
            continue

        print(f"[ANSWER] {answer}")

        result = submit_answer(
            puzzle["id"],
            answer
        )

        # Cek hasil dan ekstrak total balance
        if result.get("correct"):
            current_balance = result.get("balance", "Unknown")
            print(f"💰 [SUCCESS] +500 NTC | Total Saldo Saat Ini: {current_balance} NTC")
        else:
            print(f"❌ [FAILED] Wrong answer. Result: {result}")
            # Opsional: Jika AI salah menebak, hapus dari cache agar dia mencoba lagi nanti
            prompt_key = puzzle["prompt"]
            if prompt_key in cache:
                del cache[prompt_key]
                save_cache()

        time.sleep(5)

    except Exception as e:
        print(f"[ERROR] Connection/System issue: {e}")
        time.sleep(15)
