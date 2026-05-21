import os
import shutil
import subprocess


RESULTS_DIR = os.path.join("reports", "allure-results")


def main():
    if os.path.exists(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    command = [
        "behave",
        "-f",
        "allure_behave.formatter:AllureFormatter",
        "-o",
        RESULTS_DIR,
    ]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
