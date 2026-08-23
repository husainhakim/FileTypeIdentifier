# FileIdentifier 🔍

🌐 **Live Demo / Hosted App**: [https://file-type-identifier.vercel.app/](https://file-type-identifier.vercel.app/)

**FileIdentifier** is a cybersecurity tool designed to identify the true file type of a file by analyzing its "magic numbers" (file signatures) rather than relying on its file extension. This is critical in cybersecurity for detecting spoofed files or potential malware hiding behind fake extensions.

## 🚀 Features

- **True File Type Detection**: Reads the binary header of a file to match against a database of 30+ common file signatures (PDF, PNG, ZIP, ELF, MZ, etc.).
- **Spoofing Detection**: Automatically compares the true file signature against the file's claimed extension and alerts the user if a mismatch is found.
- **Forensics Hex Viewer**: Displays a raw hex dump of the file's first 256 bytes (offsets, hex bytes, and ASCII representation).
- **Asymmetric Forensics-Lab UI**: A custom-built, brutalist React frontend designed to look like a true terminal/forensics tool, completely avoiding generic web templates.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, Vite, Vanilla CSS

## 💻 Running Locally

### 1. Start the Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

### 2. Start the Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

### 3. Use the App
Navigate to `http://localhost:5173` (or the port Vite provides) in your browser. Drag and drop a file into the upload zone to see its true signature and hex dump!

## 🛡️ Security Use Case
Attackers often rename a malicious executable (e.g., `payload.exe`) to a harmless document name (e.g., `invoice.pdf`) to trick users into opening it. FileIdentifier immediately flags this by reading the `MZ` (executable) magic number in the binary and alerting the user that the file is spoofed.
