from selenium.webdriver.common.by import By


class LoginLocators:
    LOGIN_BUTTON = (By.XPATH, "//button[contains(., 'Login')]")
    MOBILE_INPUT = (By.ID, "multiform")
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(text(),'Continue')]")
    OTP_HEADING = (By.XPATH, "//*[contains(text(),'Enter OTP')]")
    VERIFY_BUTTON = (
        By.XPATH,
        "//button[contains(text(),'Verify & Continue') "
        "or contains(text(),'Verify and Continue') "
        "or contains(text(),'Verify')]",
    )
    GOT_IT_BUTTON = (
        By.XPATH,
        "//button[contains(text(),'Got it') "
        "or contains(text(),'GOT IT') "
        "or contains(text(),'Got It')]",
    )

