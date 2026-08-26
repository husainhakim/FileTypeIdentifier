# Project Journey

## 1. Why I Built This

I built FileIdentifier because I wanted to understand exactly how operating systems and forensic tools identify files at the lowest level. 

I had learned that file extensions are fundamentally meaningless to an operating system—a `.exe` renamed to `.pdf` is still an executable—but I had never written code to actually verify this. I chose to build a custom project instead of just using command-line tools like `file` or `xxd` because I wanted to implement the byte-reading and hex-dump generation logic myself. I wanted to understand how to handle raw binary data in memory and translate it into something readable.

## 2. The Problem

Operating systems and users trust file extensions. If a file is named `invoice.pdf`, a user expects it to open in a PDF viewer. Attackers exploit this trust by renaming malicious executables or scripts to masquerade as harmless documents. 

If this problem is ignored, a user might double-click a fake document, executing malware because the OS blindly trusted the malicious binary structure rather than the safe-looking name. This tool addresses that by immediately checking the file's internal signature—the "magic number"—and comparing it to the extension the file claims to have.

## 3. My Approach

I built this as a web application with a React frontend and a Python FastAPI backend. 

I chose Python for the backend because it makes binary data manipulation straightforward. Instead of saving the uploaded files to disk, the API reads only the first 512 bytes of the file directly from the HTTP request into memory (`await file.read(512)`). This ensures the application is fast, stateless, and safe (since it never writes potentially malicious files to a server).

The backend iterates through a predefined dictionary of magic numbers (sorted by length to match the most specific signatures first) and checks if the file's raw bytes start with those signatures. I then built a custom brutalist, high-contrast UI in React to display the analysis and a generated hex dump.

## 4. Challenges I Faced

### Handling Polyglot Containers (ZIP files)
**The Difficulty:** I initially built the spoofing detection to strictly flag any mismatch between the true signature and the extension. However, when I uploaded a `.docx` file, it flagged it as spoofed, claiming it was a `.zip`. 
**Why it was difficult:** Modern Microsoft Office documents (DOCX, XLSX), Java Archives (JAR), and Android Packages (APK) are literally just ZIP files with a specific folder structure. Their magic number is `PK\x03\x04`. 
**The Solution:** I had to implement specific whitelisting logic. If the backend detects a `zip` signature but the file claims to be a `docx`, `jar`, or `apk`, the API explicitly allows it to pass without triggering the spoofing alert.

### Vercel Serverless Integration
**The Difficulty:** Hosting a Python backend and a Node-based React frontend usually requires two separate servers.
**The Solution:** I restructured the project to deploy on Vercel by moving the FastAPI application into an `api/index.py` file. This allowed Vercel to treat the Python backend as Serverless Functions alongside the Vite frontend build, significantly simplifying deployment, though it required updating the routing logic.

## 5. What I Learned

### Technical
- **Binary I/O:** I learned how to read files as raw bytes (`b""`) in Python and how to convert those bytes into zero-padded hexadecimal strings (`f"{b:02x}"`) for the hex viewer.
- **Magic Numbers:** I learned the specific hex signatures for common formats (e.g., `%PDF` for PDFs, `MZ` for Windows executables, `\x7FELF` for Linux binaries).

### Problem Solving
- **Edge Cases in Security:** The ZIP polyglot issue taught me that security rules cannot always be strictly binary. I had to research the actual file specifications of Office documents to understand why my initial logic was failing and design a secure whitelist to fix it.

### Engineering
- **Stateless APIs:** I learned how to process file uploads entirely in memory using FastAPI's `UploadFile`. This prevents the server from filling up with junk data and mitigates risks associated with storing untrusted user files.

## 6. What I Would Improve

If I continue developing this tool, I would prioritize:
1. **Deeper Signature Parsing (Accuracy):** Currently, the tool stops at identifying a ZIP container. I would improve the Python parser to actually read the ZIP headers in memory and look for files like `[Content_Types].xml` to confirm it is genuinely a DOCX, rather than just trusting the whitelist.
2. **Larger Magic Number Database (Usability):** The current dictionary is limited to about 30 common formats. Expanding this or integrating an existing database like `python-magic` (libmagic) would make it much more robust.
3. **Frontend Chunking (Performance):** If I wanted to calculate full file hashes (like SHA-256) for malware correlation in the future, reading the whole file into memory at once would crash the server for large files. I would need to implement chunked file reading.

## 7. What This Project Taught Me About the Real World

This project demonstrated exactly why signature-based antivirus scanners work the way they do, and why they are sometimes easily bypassed. 

It also highlighted the tension between convenience and security. The fact that the tech industry decided to make DOCX files out of ZIP files makes software development easier, but it makes forensics and file validation significantly harder because the boundaries between file types are blurred.

## 8. Final Takeaway

FileIdentifier was worth building because it demystified what happens when a computer opens a file. The most important thing I learned is how to confidently handle and format raw memory/binary data. This project has prepared me to dive deeper into malware analysis, reverse engineering, or building more complex network packet parsers.
