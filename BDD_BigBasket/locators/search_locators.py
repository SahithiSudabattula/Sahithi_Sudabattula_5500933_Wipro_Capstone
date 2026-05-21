from selenium.webdriver.common.by import By


class SearchLocators:
    SEARCH_BOX = (
        By.XPATH,
        "//input[@type='search' "
        "or contains(@placeholder,'Search') "
        "or contains(@class,'search')]",
    )
    ADD_BUTTON = (
        By.XPATH,
        "(//button[contains(text(),'Add') or contains(text(),'ADD')])[1]",
    )
    ALL_ADD_BUTTONS = (
        By.XPATH,
        "//button[contains(text(),'Add') or contains(text(),'ADD')]",
    )
    BASKET_BUTTON = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'smart basket') "
        "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basket') "
        "or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basket')]",
    )
    CHECKOUT_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]",
    )
    BASKET_CONTENT = (
        By.XPATH,
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basket') "
        "or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout') "
        "or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cart')]",
    )
    INCREMENT_BUTTON = (By.XPATH, "(//button[contains(.,'+')])[1]")

