# This file is part of CF1400 Downloader.
# Copyright (C) 2025 Ray Stiegler
# Licensed under the GNU General Public License v3.0
# See LICENSE file for details.

from fastapi import FastAPI
from cf1400_downloader import CF1400Downloader

app = FastAPI()
downloader = CF1400Downloader()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/download")
def download_next_file():
    latest_entry = downloader.get_latest_cf1400_entry()

    if latest_entry:
        year, month, _ = latest_entry
    else:
        year = downloader.start['year']
        month = downloader.start['month']

    filename = downloader.download_cf1400_file(year, month)

    if filename:
        return {"success": True, "filename": filename}
    else:
        return {"success": False, "message": "No CF1400 file found"}
