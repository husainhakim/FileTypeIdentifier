from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from signatures import identify_signature

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_hex_dump(data: bytes, length: int = 256) -> list:
    """
    Generates a hex dump of the first `length` bytes.
    Format: [{'offset': '00000000', 'hex': '89 50 4E 47 ...', 'ascii': '.PNG...'}]
    """
    dump = []
    chunk_size = 16
    for i in range(0, min(len(data), length), chunk_size):
        chunk = data[i:i+chunk_size]
        offset = f"{i:08x}"
        hex_bytes = " ".join(f"{b:02x}" for b in chunk)
        
        # Pad hex bytes if less than 16
        if len(chunk) < chunk_size:
            hex_bytes += "   " * (chunk_size - len(chunk))
            
        ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        
        dump.append({
            "offset": offset,
            "hex": hex_bytes.strip(),
            "ascii": ascii_chars
        })
    return dump

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # Read first 512 bytes for signature detection
    header_bytes = await file.read(512)
    
    # Identify signature
    matches = identify_signature(header_bytes)
    
    # Check for spoofing
    # Extract extension from filename (e.g., "document.pdf" -> "pdf")
    filename = file.filename or ""
    parts = filename.lower().rsplit(".", 1)
    claimed_ext = parts[-1] if len(parts) > 1 else ""
    
    best_match = matches[0]
    detected_ext = best_match["ext"]
    
    is_spoofed = False
    spoof_alert = ""
    
    if detected_ext != "unknown" and claimed_ext:
        # Some mappings (like docx/zip) are tricky, but for beginner level we will do a basic check.
        # If it's a zip container, we might not want to flag docx/jar as spoofed easily.
        # But we'll just flag if there is a strict mismatch and it's not a generic container.
        zip_based = ["zip", "jar", "docx", "xlsx", "pptx", "apk"]
        if detected_ext == "zip" and claimed_ext in zip_based:
            pass # Valid
        elif detected_ext == "doc" and claimed_ext in ["doc", "xls", "ppt"]:
            pass # Valid
        elif detected_ext == "exe" and claimed_ext in ["exe", "dll", "sys"]:
            pass # Valid
        elif detected_ext != claimed_ext:
            is_spoofed = True
            spoof_alert = f"SPOOFING DETECTED: File claims to be .{claimed_ext} but is actually a {detected_ext.upper()}."

    # Create hex dump
    hex_dump = create_hex_dump(header_bytes, length=256)
    
    return {
        "filename": filename,
        "matches": matches,
        "is_spoofed": is_spoofed,
        "spoof_alert": spoof_alert,
        "hex_dump": hex_dump
    }
