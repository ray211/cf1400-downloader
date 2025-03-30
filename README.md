# CF1400 Downloader Microservice

This is a Python-based microservice for downloading and managing **U.S. Customs CF 1400** (Record of Vessel in Foreign Trade – Entrances) PDF reports from the U.S. Customs and Border Protection (CBP) website.

It is designed to:
- Track which CF1400 files have already been downloaded and processed
- Download new files automatically based on configuration or database history
- Convert them into structured data (planned)
- Serve as a backend service that can be used manually or triggered via API

---

## 📄 What is a CF 1400 File?

The **CF 1400** (U.S. Customs Form 1400) is a document used by the U.S. Customs and Border Protection to record information about **vessels entering U.S. ports in foreign trade**.

These PDF files contain vessel names, ports of arrival, dates of entrance, and other shipping metadata. They're important for:
- Maritime trade compliance and oversight
- Port traffic and logistics analytics
- Historical tracking of international shipping activity

CBP publishes these forms monthly or quarterly in PDF format.

---

## ⚙️ Features

- Reads config from `configuration.yaml`
- Connects to a Postgres database to check download history
- Automatically figures out the next report to download
- Tries multiple URL patterns to locate the correct PDF
- Saves files into a specified folder, with structured naming
- Built-in logging and exception handling
- Exposed as a FastAPI microservice (optional)

---

## 🚀 How to Use

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
