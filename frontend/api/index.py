from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# Common Magic Numbers (File Signatures)
# Maps hex signature -> (Extension, Description)
MAGIC_NUMBERS = {
    # Documents / Office
    b"%PDF": ("pdf", "PDF Document"),
    b"PK\x03\x04": ("zip", "ZIP Archive (or JAR/DOCX/XLSX)"),
    b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1": ("doc", "Microsoft Office OLE2 (DOC/XLS/PPT)"),
    b"{\\rtf1": ("rtf", "Rich Text Format"),

    # Images
    b"\x89PNG\x0D\x0A\x1A\x0A": ("png", "PNG Image"),
    b"\xFF\xD8\xFF": ("jpg", "JPEG Image"),
    b"GIF87a": ("gif", "GIF Image (87a)"),
    b"GIF89a": ("gif", "GIF Image (89a)"),
    b"BM": ("bmp", "BMP Image"),
    b"II*\x00": ("tif", "TIFF Image (Little Endian)"),
    b"MM\x00*": ("tif", "TIFF Image (Big Endian)"),
    b"RIFF": ("webp", "WebP Image (assuming WEBP in chunk)"),

    # Executables / Binaries
    b"\x7FELF": ("elf", "Executable and Linkable Format (Linux)"),
    b"MZ": ("exe", "DOS/Windows Executable"),
    b"\xCE\xFA\xED\xFE": ("macho", "Mach-O Binary (32-bit)"),
    b"\xCF\xFA\xED\xFE": ("macho", "Mach-O Binary (64-bit)"),
    b"\xCA\xFE\xBA\xBE": ("class", "Java Class File / Mach-O Fat Binary"),

    # Audio/Video
    b"ID3": ("mp3", "MP3 Audio (ID3v2)"),
    b"\xFF\xFB": ("mp3", "MP3 Audio (MPEG ADTS)"),
    b"OggS": ("ogg", "Ogg Vorbis Audio"),
    b"fLaC": ("flac", "FLAC Audio"),
    b"\x00\x00\x00\x18ftyp": ("mp4", "MP4 Video"),
    
    # Archives / Compressed
    b"\x1F\x8B\x08": ("gz", "GZIP Archive"),
    b"BZh": ("bz2", "Bzip2 Archive"),
    b"Rar!\x1A\x07\x00": ("rar", "RAR Archive (v1.5)"),
    b"Rar!\x1A\x07\x01\x00": ("rar", "RAR Archive (v5.0)"),
    b"\xFD7zXZ\x00": ("xz", "XZ Archive"),
    b"7z\xBC\xAF\x27\x1C": ("7z", "7-Zip Archive"),
    b"\x1F\x9D": ("tar.z", "Compressed Tape Archive"),

    # Misc
    b"%!PS": ("ps", "PostScript"),
    b"SQLite format 3\x00": ("sqlite", "SQLite Database"),
    b"ITSF": ("chm", "Microsoft Compiled HTML Help"),
}

def identify_signature(file_bytes: bytes):
    """
    Scans the beginning of the file bytes to find a matching magic number.
    Returns a list of matches. (List allows for multiple matches if they share prefixes, though our DB has unique prefixes here)
    """
    matches = []
    # Sort keys by length descending to match longest signature first
    sorted_signatures = sorted(MAGIC_NUMBERS.keys(), key=len, reverse=True)
    
    for sig in sorted_signatures:
        if file_bytes.startswith(sig):
            ext, desc = MAGIC_NUMBERS[sig]
            # Extra logic for ZIP since it's a polyglot container
            if ext == "zip":
                matches.append({"ext": "zip", "description": desc, "confidence": 0.8})
            elif ext == "exe":
                 matches.append({"ext": "exe", "description": desc, "confidence": 0.9})
            else:
                matches.append({"ext": ext, "description": desc, "confidence": 1.0})
            
            # Since we matched the longest possible first, we can return or continue for polyglots.
            # For beginner level, we will just break after the best match.
            break
            
    if not matches:
        return [{"ext": "unknown", "description": "Unknown File Type", "confidence": 0.0}]
        
    return matches

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
