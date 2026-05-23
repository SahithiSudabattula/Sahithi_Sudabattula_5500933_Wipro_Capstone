import logging
import os
import sys


class LogGen:
    @staticmethod
    def loggen():
        os.makedirs("logs", exist_ok=True)
        logger = logging.getLogger("AutomationLogger")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )

            file_handler = logging.FileHandler(
                "logs/automation.log", mode="a", encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler(
                stream=open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        logger.propagate = False

        return logger
