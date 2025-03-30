# This file is part of CF1400 Downloader.
# Copyright (C) 2025 Ray Stiegler
# Licensed under the GNU General Public License v3.0
# See LICENSE file for details.

import os
import calendar
import logging
import requests
import psycopg2
import yaml
import datetime
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse, unquote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CF1400Downloader:
    """
    A class to handle downloading CF1400 PDF files from US Customs website,
    based on configuration and database state.
    """

    def __init__(self, config_path='configuration.yaml'):
        self.config = self.load_config(config_path)
        self.db_config = self.config['database']
        self.start = self.config['start']
        self.cf1400 = self.config['cf1400']

    def load_config(self, path: str) -> dict:
        """Loads configuration from a YAML file."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
        
    def get_quarter(self, month: int) -> int:
        return ((month - 1) // 3) + 1
        
    def record_downloaded_file(self, year: int, month: int, quarter: int, filename: str, url: str):
        """
        Inserts a record into the cf1400_files table after a successful download.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO cf1400_files (year, month, quarter, pdf_filename, file_url, downloaded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                year, month, quarter, filename, url, datetime.datetime.now()
            ))

            conn.commit()
            cur.close()
            conn.close()
            print(f"[DB] Recorded file in database: {filename}")
        except Exception as e:
            print(f"[DB ERROR] Failed to record {filename}: {e}")
            

    def get_latest_cf1400_entry(self) -> Optional[Tuple[int, int, int]]:
        """
        Retrieves the most recent (year, month, quarter) from the cf1400_files table.
        Returns None if the table is empty or an error occurs.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("""
                SELECT year, month, quarter
                FROM cf1400_files
                ORDER BY year DESC, month DESC, quarter DESC
                LIMIT 1;
            """)
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result if result else None
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return None

    def get_next_year_month(self, year: int, month: int) -> Tuple[int, int]:
        """Calculates the next (year, month)."""
        return (year + 1, 1) if month == 12 else (year, month + 1)

    def extract_filename_from_url(self, url: str, year: int, month: int) -> str:
        """
        Extracts the filename from a URL and prefixes it with year and month.
        """
        parsed = urlparse(url)
        original_filename = unquote(os.path.basename(parsed.path))
        month_str = f"{month:02d}"
        return f"{year}-{month_str}_{original_filename}"

    def generate_cf1400_relative_paths(self, year: int, month: int, suffixes=None) -> list:
        """
        Generates possible relative paths for CF1400 files.
        """
        if suffixes is None:
            suffixes = ["", "_2"]

        month_str = f"{month:02d}"
        month_short = calendar.month_abbr[month]

        paths = [f"{year}-{month_str}", f"{year}-{month_short}"]
        relative_paths = []

        for path in paths:
            for suffix in suffixes:
                filename = f"{self.cf1400['filename_base']}{suffix}.pdf".replace(" ", "%20")
                relative_paths.append(f"{path}/{filename}")
        return relative_paths

    def download_cf1400_file(self, year: int, month: int) -> Optional[str]:
        """
        Attempts to download a CF1400 file using known base URLs.
        Returns the filename if successful, otherwise None.
        """
        base_urls = self.cf1400['base_urls']
        download_dir = self.cf1400['download_dir']
        os.makedirs(download_dir, exist_ok=True)

        for base_url in base_urls:
            for relative_path in self.generate_cf1400_relative_paths(year, month):
                full_url = urljoin(base_url.rstrip('/') + '/', relative_path.lstrip('/'))
                filename = self.extract_filename_from_url(full_url, year, month)
                save_path = os.path.join(download_dir, filename)

                if os.path.exists(save_path):
                    logger.info(f"File already exists at {save_path}. Skipping download.")
                    return filename

                logger.info(f"Trying {full_url}...")
                try:
                    response = requests.get(full_url, stream=True, timeout=10)
                    if response.status_code == 404:
                        logger.info(f"404 Not Found: {full_url}")
                        continue

                    response.raise_for_status()
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info(f"File saved to {save_path}")
                    self.record_downloaded_file(year, month, self.get_quarter(month), filename, full_url)
                    return filename

                except requests.exceptions.HTTPError as e:
                    logger.warning(f"HTTP error for {full_url}: {e}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Network error for {full_url}: {e}")
                except OSError as e:
                    logger.error(f"File system error saving {filename}: {e}")
                    return None

        logger.warning("All download attempts failed.")
        return None

if __name__ == "__main__":
    downloader = CF1400Downloader()
    latest_entry = downloader.get_latest_cf1400_entry()

    if latest_entry:
        logger.info(f"Most recent entry in DB: {latest_entry}")
    else:
        logger.info("No entries found in cf1400_files. Using configuration start values.")
        latest_entry = (
            downloader.start['year'],
            downloader.start['month'],
            downloader.start['quarter']
        )

    filename = downloader.download_cf1400_file(latest_entry[0], latest_entry[1])
    if filename:
        logger.info(f"Downloaded: {filename}")
    else:
        logger.warning("CF1400 file not found.")

    logger.info("Completed execution")
