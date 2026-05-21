import os
import re
from datetime import datetime


class ScreenshotUtil:
    @staticmethod
    def capture_screenshot(driver, scenario_name):
        os.makedirs("screenshots", exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", scenario_name).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("screenshots", f"{safe_name}_{timestamp}.png")
        driver.save_screenshot(path)
        return path

