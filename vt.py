import requests
import re

# -----------------------------
# CONFIG
# -----------------------------
SOURCE_M3U = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"
LOCAL_M3U  = "/storage/emulated/0/qpython/scripts3/ak.m3u"
# -----------------------------

# Function to fetch source M3U (SSL issues ignore)
def fetch_source_m3u(url):
    resp = requests.get(url, verify=False, timeout=15)  # verify=False bypass SSL errors
    resp.raise_for_status()
    return resp.text

# Function to extract hdntl token from a line
def extract_hdntl_token(line):
    match = re.search(r'Cookie="(hdntl=[^"&]+)"', line)
    if match:
        return match.group(1)
    return None

# Fetch source M3U and extract token
print("Fetching source M3U...")
source_content = fetch_source_m3u(SOURCE_M3U)
token_line = None
for line in source_content.splitlines():
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

# Update each URL with latest token
new_lines = []
for line in local_lines:
    if line.startswith("http"):
        # Remove old hdntl token if present
        if "hdntl=" in line:
            line = re.sub(r'hdntl=[^&"\n]+', token_line, line)
        else:
            # Append token at the end
            line = line.strip() + f"|Cookie=\"{token_line}\"\n"
    new_lines.append(line)

# Save updated M3U
with open(LOCAL_M3U, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ Local M3U updated successfully!")
