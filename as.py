import requests
from pathlib import Path

# === CONFIG ===
URL = "https://zee5.joker-verse.workers.dev/master.m3u8?id=0-9-zing&uid=1045595420&pass=169ae613"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Origin": "https://www.zee5.com",
    "Referer": "https://www.zee5.com/",
    "X-User-Agent": "TiviMate/5.1.0 (Android 13)",
}

OUTPUT_FILE = Path("ak.txt")

def main():
    try:
        print("Requesting:", URL)
        # Allow redirect to get final m3u8 URL
        resp = requests.get(URL, headers=HEADERS, timeout=15, allow_redirects=True)
        final_url = resp.url

        if ".m3u8?" not in final_url:
            print("❌ Redirected but final URL doesn't contain token.")
            print("Final URL:", final_url)
            return

        OUTPUT_FILE.write_text(final_url, encoding="utf-8")
        print("✅ Final m3u8 link saved to:", OUTPUT_FILE)
        print("🔗", final_url)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
