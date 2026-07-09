import csv
import os
import sys
import urllib.request
import urllib.error
import concurrent.futures

# Reconfigure stdout to support UTF-8 on Windows consoles to prevent UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
except AttributeError:
    pass # Older Python versions might not have reconfigure

# Target directories
SVG_DIR = 'svg'
os.makedirs(SVG_DIR, exist_ok=True)

# 1. Collect all characters
characters = set()

# Load Kanji from kanji.csv
if os.path.exists('kanji.csv'):
    with open('kanji.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader) # Skip header
        for row in reader:
            if row:
                characters.add(row[0].strip())

# Load Kanji from vocab.csv
if os.path.exists('vocab.csv'):
    with open('vocab.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader) # Skip header
        for row in reader:
            if row:
                word = row[0].strip()
                for char in word:
                    # Check if character is a Kanji (CJK Unified Ideographs range 0x4E00 to 0x9FAF)
                    if 0x4E00 <= ord(char) <= 0x9FAF:
                        characters.add(char)

# Add all Hiragana (0x3041 - 0x3096)
for i in range(0x3041, 0x3097):
    characters.add(chr(i))

# Add all Katakana (0x30A1 - 0x30FB)
for i in range(0x30A1, 0x30FB):
    characters.add(chr(i))

print(f"Total unique characters to check: {len(characters)}")

# 2. Downloader function
def download_character(char):
    # Convert to hex string padded to 5 chars (e.g. 04e00)
    codepoint = ord(char)
    unicode_str = f"{codepoint:05x}"
    filename = os.path.join(SVG_DIR, f"{unicode_str}.svg")
    
    # Skip if already exists
    if os.path.exists(filename):
        return char, "exists"
        
    url = f"https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/{unicode_str}.svg"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            svg_text = response.read().decode('utf-8')
            
        # Clean SVG: Strip DOCTYPE and XML declaration
        svg_start = svg_text.find('<svg')
        if svg_start != -1:
            svg_text = svg_text[svg_start:]
            
        # Inject xmlns:kvg namespace definition on root <svg> element if missing
        if 'xmlns:kvg' not in svg_text:
            svg_text = svg_text.replace('<svg', '<svg xmlns:kvg="http://kanjivg.tagaini.net"')
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_text)
            
        return char, "downloaded"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return char, f"404 ({unicode_str})"
        else:
            return char, f"error {e.code}"
    except Exception as e:
        return char, f"error: {str(e)}"

# Download characters concurrently
print("Starting concurrent downloads...")
results = {"downloaded": 0, "exists": 0, "failed": []}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_char = {executor.submit(download_character, char): char for char in characters}
    for future in concurrent.futures.as_completed(future_to_char):
        char = future_to_char[future]
        try:
            char, status = future.result()
            if status == "downloaded":
                results["downloaded"] += 1
                print(f"Downloaded: U+{ord(char):05x} ({char})")
            elif status == "exists":
                results["exists"] += 1
            else:
                results["failed"].append((char, status))
                print(f"Failed to fetch U+{ord(char):05x} ({char}): {status}")
        except Exception as exc:
            results["failed"].append((char, f"exception: {str(exc)}"))
            print(f"Exception for U+{ord(char):05x}: {exc}")

print("\n--- Download Summary ---")
print(f"Downloaded: {results['downloaded']}")
print(f"Already existed: {results['exists']}")
print(f"Failed/Missing: {len(results['failed'])}")
for char, reason in results["failed"]:
    print(f"  - U+{ord(char):05x} ({char}): {reason}")
