import requests
import re
import shutil
from pathlib import Path
import time

# ---------------- CONFIG ----------------
SOURCE_URL = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"
AK_FILE = "ak.m3u"          # file to update in-place
BACKUP_SUFFIX = ".bak"      # backup file
HEADERS = {
    "Host": "joker-verse.vercel.app",
    "User-Agent": "TiviMate/5.1.0 (Android 13)",
    "Accept-Encoding": "gzip",
    "Connection": "keep-alive"
}
RETRIES = 5
TIMEOUT = 300
CHUNK_SIZE = 8192
# ---------------------------------------

def download_source(url, headers, retries=RETRIES, timeout=TIMEOUT):
    """Download source playlist text with retries."""
    for attempt in range(1, retries + 1):
        try:
            print(f"[Download] Attempt {attempt}...")
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"[Download] Error: {e}, retrying...")
            time.sleep(3)
    raise RuntimeError("Failed to download source playlist after retries")

def extract_token(source_text, base_url=None):
    """Extract hdntl token for given base_url. If no base_url given, return first token found."""
    if base_url:
        # Try to find token near base_url
        for m in re.finditer(re.escape(base_url), source_text):
            start = max(0, m.start() - 300)
            end = m.end() + 1500
            snippet = source_text[start:end]
            tok = re.search(r'hdntl=[^"&\s\|]+', snippet)
            if tok:
                return tok.group(0)
    # fallback: first token in source
    tok = re.search(r'hdntl=[^"&\s\|]+', source_text)
    if tok:
        return tok.group(0)
    return None

def update_ak_m3u(ak_file, source_text):
    """Update ak.m3u in-place with new tokens"""
    p = Path(ak_file)
    if not p.exists():
        raise FileNotFoundError(f"{ak_file} not found")

    # Backup
    backup_path = p.with_suffix(p.suffix + BACKUP_SUFFIX)
    shutil.copy2(p, backup_path)
    print(f"[Backup] Saved backup: {backup_path}")

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    updated_lines = []
    total_http = 0
    updated_count = 0

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("http"):
            total_http += 1
            # Extract base URL (cut at ? or | if present)
            q_idx = len(stripped)
            for delim in ['?', '|']:
                i = stripped.find(delim)
                if i != -1:
                    q_idx = min(q_idx, i)
            base = stripped[:q_idx]
            token = extract_token(source_text, base)
            if token:
                new_line = base + "?" + token + ("\n" if not line.endswith("\n") else "")
                updated_lines.append(new_line)
                updated_count += 1
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    # Write back in-place
    p.write_text("".join(updated_lines), encoding="utf-8")
    print(f"[Done] Total channels: {total_http}, Updated: {updated_count}")

if __name__ == "__main__":
    print("1) Downloading source playlist...")
    src_text = download_source(SOURCE_URL, HEADERS)
    print("2) Updating ak.m3u in-place...")
    update_ak_m3u(AK_FILE, src_text)
    print("✅ Finished.")
