import csv
import os
from utils.logger import LogGen

logger = LogGen.loggen()


class CSVReader:

    @staticmethod
    def read_csv(filename):
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "test_data", filename
        )
        filepath = os.path.abspath(filepath)
        logger.info(f"Reading CSV: {filepath}")
        rows = []
        try:
            with open(filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
            logger.info(f"CSV loaded: {len(rows)} rows from {filename}")
        except FileNotFoundError:
            logger.error(f"CSV not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            raise
        return rows