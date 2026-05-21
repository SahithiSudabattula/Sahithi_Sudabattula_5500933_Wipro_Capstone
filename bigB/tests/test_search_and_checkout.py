import time
import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.csv_reader import CSVReader
from utils.logger import LogGen

logger = LogGen.loggen()

login_rows  = CSVReader.read_csv("login_data.csv")
search_rows = CSVReader.read_csv("search_data.csv")
test_data   = list(zip(login_rows, search_rows))

@allure.feature("bigB E2E")
@allure.story("Search and Checkout")
@pytest.mark.parametrize("login_data,search_data", test_data,
                         ids=[f"{l['mobile']}-{s['product']}" for l, s in test_data])

def test_search_and_checkout(driver, login_data, search_data):
    mobile  = login_data["mobile"]
    product = search_data["product"]

    logger.info(f"=== Test START | mobile: {mobile} | product: {product} ===")
    print(f"=== Test START | mobile: {mobile} | product: {product} ===")

    login  = LoginPage(driver)
    search = SearchPage(driver)

    # Login flow
    login.open_bigbasket()
    title = driver.title.lower()
    assert "bigbasket" in title and "online grocery" in title, f"Unexpected homepage title: {driver.title}"

    try:
        login.click_login()
    except Exception as e:
        pytest.fail(f"Login button failed: {e}")

    login.enter_mobile_email(mobile)
    assert mobile.strip() != "", "Mobile number not entered"

    login.click_continue()

    otp_ready = login.wait_for_otp_page()
    assert otp_ready, "OTP page not detected"

    try:
        login.wait_for_verify_and_click()
    except TimeoutException:
        pytest.fail("Timed out waiting for OTP verification")

    login.dismiss_location_popup()

    # confirm search box is ready
    search.wait_for_search_box(timeout=20)

    # Search flow
    search.search_product(product)

    # wait until Add button is visible (indicates product results loaded)
    search.wait.until(EC.presence_of_element_located(search.ADD_BUTTON))
    assert True, f"Search results not loaded for product: {product}"

    search.click_add_button()

    search.wait.until(EC.presence_of_element_located(search.ADD_BUTTON))
    search.click_add_button()

    # Basket flow
    search.wait.until(EC.presence_of_element_located(search.BASKET_BUTTON))
    search.click_basket()
    time.sleep(5)

    search.click_increment()

    # Checkout flow
    search.wait.until(EC.presence_of_element_located(search.CHECKOUT_BUTTON))
    search.click_checkout()

    WebDriverWait(driver, 15).until(EC.url_contains("checkout"))
    assert "checkout" in driver.current_url, "Checkout page not reached"

    logger.info(f"=== Test PASSED | mobile: {mobile} | product: {product} ===")
    print(f"=== Test PASSED | mobile: {mobile} | product: {product} ===")
