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
    b"RIFF": ("webp", "WebP Image (assuming WEBP in chunk)"), # Simplified, actual is RIFF...WEBP

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
