from selenium.webdriver.common.by import By


class SearchLocators:
    SEARCH_BOX      = (
        By.XPATH,
        "//input[@type='search' "
        "or contains(@placeholder,'Search') "
        "or contains(@class,'search')]",
    )
    ADD_BUTTON      = (
        By.XPATH,
        "(//button[contains(text(),'Add') or contains(text(),'ADD')])[1]",
    )
    ALL_ADD_BUTTONS = (
        By.XPATH,
        "//button[contains(text(),'Add') or contains(text(),'ADD')]",
    )
    AUTOCOMPLETE_LIST = (
        By.XPATH,
        "//ul[contains(@class,'suggest') or contains(@class,'autocomplete')]",
    )
    BASKET_BUTTON   = (
        By.XPATH,
        "("
        "//div[contains(@class,'bg-rossoCorsa-50') and contains(@class,'cursor-pointer')] | "
        "//div[contains(@class,'bg-rossoCorsa-50') and .//*[name()='svg']] | "
        "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basket')] | "
        "//*[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basket')]"
        ")[1]",
    )
    CHECKOUT_BUTTON = (
        By.XPATH,
        "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]",
    )
    ADDRESS_DIV     = (
        By.XPATH,
        "(//div[contains(@class,'address-item') or contains(@class,'AddressCard')])[1]",
    )
    BASKET_CONTENT = (
        By.XPATH,
        "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]",
    )
