import logging
import os
import sys


class LogGen:

    @staticmethod
    def loggen():
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger("AutomationLogger")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # utf-8 encoding on file handler fixes ₹ and other unicode chars
            file_handler = logging.FileHandler(
                "logs/automation.log", encoding="utf-8"
            )
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Console handler also set to utf-8 to avoid cp1252 crash on Windows
            console_handler = logging.StreamHandler(
                stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger