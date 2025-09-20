import requests
import re

# -----------------------------
# CONFIG
# -----------------------------
SOURCE_M3U = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"
LOCAL_M3U  = "ak.m3u"

# Custom headers
HEADERS = {
    "User-Agent": "TiviMate/5.1.0 (Android 11)"
}
# -----------------------------

# Function to fetch source M3U content
def fetch_source_m3u(url):
    resp = requests.get(url, headers=HEADERS, verify=False, timeout=15)  # headers + SSL bypass
    resp.raise_for_status()
    return resp.text

# Function to extract latest hdntl token from a line
def extract_hdntl_token(line):
    # Regex to find hdntl token in Cookie=""
    match = re.search(r'Cookie="(hdntl=[^"&]+)"', line)
    if match:
        return match.group(1)
    return None

# Read source M3U and extract token
source_content = fetch_source_m3u(SOURCE_M3U)
lines = source_content.splitlines()
token_line = None
for line in lines:
    token = extract_hdntl_token(line)
    if token:
        token_line = token
        break

if not token_line:
    print("❌ Token not found in source M3U!")
    exit()

print("✅ Latest Token:", token_line)

# Read local M3U
with open(LOCAL_M3U, "r", encoding="utf-8") as f:
    local_lines = f.readlines()

# Replace each URL's hdntl token in local M3U
new_lines = []
for line in local_lines:
    if line.startswith("http"):
        # Remove existing hdntl token if present
        if "hdntl=" in line:
            line = re.sub(r'hdntl=[^&"\n]+', token_line, line)
        else:
            # Append token at the end
            line = line.strip() + f'|Cookie="{token_line}"\n'
    new_lines.append(line)

# Save updated M3U
with open(LOCAL_M3U, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ Local M3U updated successfully!")
