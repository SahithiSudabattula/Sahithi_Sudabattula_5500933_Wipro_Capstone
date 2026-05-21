import csv
import os

from utils.logger import LogGen


logger = LogGen.loggen()


class CSVReader:
    @staticmethod
    def test_data_dir():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_data"))

    @staticmethod
    def read_csv(filename):
        filepath = os.path.join(CSVReader.test_data_dir(), filename)
        logger.info("Reading CSV: %s", filepath)

        rows = []
        with open(filepath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(dict(row))

        logger.info("CSV loaded: %s rows from %s", len(rows), filename)
        return rows

    @staticmethod
    def read_required_csv(filename):
        rows = CSVReader.read_csv(filename)
        assert rows, f"{filename} must contain at least one data row"
        return rows

    @staticmethod
    def values(filename, column, required=True):
        rows = CSVReader.read_required_csv(filename) if required else CSVReader.read_csv(filename)
        values = [row.get(column, "").strip() for row in rows if row.get(column, "").strip()]
        if required:
            assert values, f"{filename} must contain values in '{column}' column"
        return values

    @staticmethod
    def read_all_csv_files():
        data_dir = CSVReader.test_data_dir()
        csv_data = {}
        for filename in sorted(os.listdir(data_dir)):
            if filename.lower().endswith(".csv"):
                csv_data[filename] = CSVReader.read_csv(filename)
        assert csv_data, f"No CSV files found in {data_dir}"
        return csv_data
