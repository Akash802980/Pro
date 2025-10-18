
import time
import requests
import re
from pathlib import Path

# ===== CONFIG =====
WORKER_URL = "https://zee5.joker-verse.workers.dev/master.m3u8?id=0-9-zing&uid=1045595420&pass=169ae613"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Origin": "https://www.zee5.com",
    "Referer": "https://www.zee5.com/",
    "X-User-Agent": "TiviMate/5.1.0 (Android 13)",
}
OUTPUT_FILE = Path("ak.txt")

# Polling settings
INTERVAL_SEC = 30           # wait time between tries (seconds)
MAX_DURATION_SEC = 120      # total max time to keep trying (seconds)
REQUEST_TIMEOUT = 15        # HTTP request timeout (seconds)

# Optional: pattern to identify desired z5 CDN link (adjust if needed)
Z5_PATTERN = re.compile(r"https?://[^\s'\"<>]*z5[a-z0-9\-._]*\.zee5\.com[^\s'\"<>]*\.m3u8\?[^ \r\n'\"<>]+", re.IGNORECASE)
# generic tokened m3u8 fallback pattern
M3U8_TOKEN_PATTERN = re.compile(r"https?://[^\s'\"<>]+\.m3u8\?[^ \r\n'\"<>]+", re.IGNORECASE)


def try_once():
    """
    Perform one attempt:
    - GET WORKER_URL with redirect following.
    - Check resp.url and resp.text for tokened .m3u8 link.
    Returns found_link (str) or None.
    """
    try:
        print("Requesting:", WORKER_URL)
        resp = requests.get(WORKER_URL, headers=HEADERS, allow_redirects=True, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print("Request error:", e)
        return None

    final_url = resp.url
    print(" -> Redirected to:", final_url)

    # 1) If final_url itself contains a tokened .m3u8, return it
    if ".m3u8?" in final_url:
        # prefer z5 pattern if matches
        if Z5_PATTERN.search(final_url) or M3U8_TOKEN_PATTERN.search(final_url):
            print("Found tokened .m3u8 in final URL.")
            return final_url

    # 2) If the final resource is a .m3u8 text (e.g., raw GitHub), search inside its body
    content_type = resp.headers.get("content-type", "")
    text = resp.text if resp.text else ""
    # Try to find a z5 CDN tokened link inside the content first
    m = Z5_PATTERN.search(text)
    if m:
        print("Found z5 tokened link inside content.")
        return m.group(0)

    # fallback: any .m3u8? link inside content
    m2 = M3U8_TOKEN_PATTERN.search(text)
    if m2:
        print("Found tokened .m3u8 inside content.")
        return m2.group(0)

    # nothing found this attempt
    print("No tokened .m3u8 found on this attempt.")
    # Optionally save debug snapshot for inspection (uncomment if needed)
    # with open("debug_snapshot.txt", "w", encoding="utf-8") as f: f.write(text[:20000])
    return None


def main():
    start = time.time()
    end_time = start + MAX_DURATION_SEC
    attempt = 0

    while time.time() <= end_time:
        attempt += 1
        print("--- Attempt", attempt, " (elapsed {:.1f}s)".format(time.time() - start))
        found = try_once()
        if found:
            # write and exit
            try:
                OUTPUT_FILE.write_text(found, encoding="utf-8")
                print("✅ Saved final link to", OUTPUT_FILE)
                print(found)
                return
            except Exception as e:
                print("Failed to write file:", e)
                return
        # not found -> maybe wait before next attempt, but stop if time exceeded
        remaining = end_time - time.time()
        if remaining <= 0:
            break
        sleep_time = min(INTERVAL_SEC, remaining)
        print("Waiting", int(sleep_time), "seconds before next try...\n")
        time.sleep(sleep_time)

    print("❌ Stopped after {:.1f} seconds. No tokened z5 link found.".format(time.time() - start))
    # optional: leave last response / debug for inspection


if __name__ == "__main__":
    main()
