import logging
import os


class LogGen:
    @staticmethod
    def loggen():
        os.makedirs("logs", exist_ok=True)
        logger = logging.getLogger("bigbasket_bdd")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )

            file_handler = logging.FileHandler("logs/automation.log", mode="a")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False

        return logger
