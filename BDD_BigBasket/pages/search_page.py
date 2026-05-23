import time
from urllib.parse import quote_plus

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.search_locators import SearchLocators
from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class SearchPage(BasePage):
    SEARCH_BOX = SearchLocators.SEARCH_BOX
    ADD_BUTTON = SearchLocators.ADD_BUTTON
    BASKET_BUTTON = SearchLocators.BASKET_BUTTON
    CHECKOUT_BUTTON = SearchLocators.CHECKOUT_BUTTON
    ADDRESS_DIV = SearchLocators.ADDRESS_DIV

    def wait_for_search_box(self, timeout=20):
        self.logger.info("Waiting for search box (timeout=%ss)", timeout)
        print(f"Waiting for search box (timeout={timeout}s)...")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                lambda driver: self._visible_enabled_element(SearchLocators.SEARCH_BOX)
            )
            self.logger.info("Search box ready")
            print("Search box ready")
            return element
        except TimeoutException as error:
            self.logger.error("Search box not found within %ss", timeout)
            raise TimeoutException("Search box not found within timeout") from error

    def _visible_enabled_element(self, locator):
        # BigBasket can render multiple matching search inputs; use the first usable one.
        elements = self.driver.find_elements(*locator)
        for element in elements:
            try:
                if element.is_displayed() and element.is_enabled():
                    return element
            except StaleElementReferenceException:
                continue
        return False

    def search_product(self, product_name):
        self.logger.info("Searching for product: %s", product_name)
        print(f"Searching for product: {product_name}")
        # Direct search URL is more stable than typing into autocomplete on this site.
        search_url = ConfigReader.get_base_url().rstrip("/") + f"/ps/?q={quote_plus(product_name)}&nc=as"
        self.driver.get(search_url)
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        self.logger.info("Search submitted: %s", product_name)
        print(f"Search submitted: {product_name}")

    def safe_click(self, locator, name="element"):
        self.logger.info("Clicking %s using locator: %s", name, locator)
        last_error = None
        for attempt in range(1, 4):
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element,
                )
                time.sleep(0.5)
                element.click()
                self.logger.info("%s clicked", name)
                print(f"{name} clicked")
                return
            except StaleElementReferenceException as error:
                last_error = error
                self.logger.warning("%s stale on attempt %s, retrying", name, attempt)
                print(f"{name} stale on attempt {attempt}, retrying...")
                time.sleep(1)
            except Exception as error:
                last_error = error
                self.logger.warning("%s normal click failed, using JS click: %s", name, error)
                print(f"{name} normal click failed, using JS click: {error}")
                try:
                    element = self.driver.find_element(*locator)
                    self.driver.execute_script("arguments[0].click();", element)
                    self.logger.info("%s clicked via JS", name)
                    print(f"{name} clicked via JS")
                    return
                except Exception:
                    time.sleep(1)
        self.logger.error("Failed to click %s after retries", name)
        raise Exception(f"Failed to click {name}") from last_error

    def click_add_button(self):
        self.logger.info("Clicking Add button")
        print("Clicking Add button...")
        last_error = None
        for attempt in range(1, 6):
            try:
                # Product cards are dynamic, so find the first visible enabled Add button in the DOM.
                clicked = self.driver.execute_script(
                    """
                    const buttons = [...document.querySelectorAll("button")]
                        .map((button) => {
                            const rect = button.getBoundingClientRect();
                            const text = (button.innerText || button.textContent || "").trim().toLowerCase();
                            const disabled = button.disabled || button.getAttribute("aria-disabled") === "true";
                            return { button, rect, text, disabled };
                        })
                        .filter(({ rect, text, disabled }) =>
                            !disabled &&
                            rect.width > 0 &&
                            rect.height > 0 &&
                            (text === "add" || text.includes("add"))
                        )
                        .sort((a, b) => a.rect.top - b.rect.top || a.rect.left - b.rect.left);

                    if (!buttons.length) return false;
                    const button = buttons[0].button;
                    button.scrollIntoView({ block: "center" });
                    button.click();
                    return true;
                    """
                )
                if clicked:
                    self.logger.info("Add button clicked")
                    print("Add button clicked")
                    time.sleep(2)
                    return
            except StaleElementReferenceException as error:
                last_error = error
                self.logger.warning("Add button stale on attempt %s, retrying", attempt)
                print(f"Add button stale on attempt {attempt}, retrying...")
            except Exception as error:
                last_error = error
                self.logger.warning("Add button click attempt %s failed: %s", attempt, error)
                print(f"Add button click attempt {attempt} failed: {error}")
            time.sleep(1)

        try:
            self.safe_click(SearchLocators.ADD_BUTTON, "Add button")
            time.sleep(2)
            return
        except Exception as error:
            self.logger.error("Failed to click Add button")
            raise Exception("Failed to click Add button") from (last_error or error)

    def click_basket(self):
        self.logger.info("Opening Basket page")
        print("Opening Basket page...")
        # Opening the basket URL avoids flaky header basket icon clicks.
        basket_url = ConfigReader.get_base_url().rstrip("/") + "/basket/?nc=nb"
        self.driver.get(basket_url)
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.logger.info("Basket page opened")
        print("Basket page opened")
        time.sleep(3)

    def _header_basket_icon(self):
        # Kept as a locator helper if direct basket navigation is replaced with a header click.
        elements = self.driver.find_elements(*SearchLocators.BASKET_BUTTON)
        width = self.driver.execute_script("return window.innerWidth || document.documentElement.clientWidth;")
        for element in elements:
            try:
                rect = element.rect
                text = (element.text or "").strip().lower()
                class_name = (element.get_attribute("class") or "").lower()
                if not element.is_displayed():
                    continue
                if rect["y"] > 80 or rect["x"] < width * 0.70:
                    continue
                if "login" in text or "sign" in text:
                    continue
                if "bg-rossocorsa-50" in class_name or "basket" in text:
                    return element
            except StaleElementReferenceException:
                continue
        return False

    def click_increment(self):
        return self.click_increment_buttons(count=1)

    def click_increment_buttons(self, count=1):
        self.logger.info("Clicking Increment button(s): %s", count)
        print(f"Clicking Increment button(s): {count}")
        clicked_count = 0
        last_error = None

        for _ in range(count):
            try:
                # The basket quantity controls change often; scan visible buttons and verify quantity change.
                clicked = WebDriverWait(self.driver, 10).until(
                    lambda driver: self.driver.execute_async_script(
                        """
                        const done = arguments[0];

                        const isVisible = (element) => {
                            const rect = element.getBoundingClientRect();
                            const style = window.getComputedStyle(element);
                            return rect.width > 0 &&
                                rect.height > 0 &&
                                style.visibility !== "hidden" &&
                                style.display !== "none";
                        };

                        const textOf = (element) =>
                            (element.innerText || element.textContent || "")
                                .replace(/\\s+/g, " ")
                                .trim()
                                .toLowerCase();

                        const asSmallNumber = (text) => {
                            const exact = String(text || "").trim().match(/^\\d{1,2}$/);
                            return exact ? Number(exact[0]) : null;
                        };

                        const getQuantity = (button) => {
                            const relatives = [
                                button.previousElementSibling,
                                button.nextElementSibling,
                                button.parentElement,
                            ].filter(Boolean);

                            const input = button.parentElement
                                ? button.parentElement.querySelector("input")
                                : null;
                            if (input && asSmallNumber(input.value) !== null) {
                                return asSmallNumber(input.value);
                            }

                            for (const element of relatives) {
                                const directNumber = asSmallNumber(textOf(element));
                                if (directNumber !== null) {
                                    return directNumber;
                                }

                                for (const child of [...element.children]) {
                                    const childNumber = asSmallNumber(textOf(child));
                                    if (childNumber !== null) {
                                        return childNumber;
                                    }
                                }
                            }

                            return null;
                        };

                        const buttons = [...document.querySelectorAll("button")]
                            .filter((button) => {
                                const label = [
                                    textOf(button),
                                    (button.getAttribute("aria-label") || "").toLowerCase(),
                                    (button.getAttribute("title") || "").toLowerCase(),
                                ].join(" ");

                                return isVisible(button) &&
                                    !button.disabled &&
                                    button.getAttribute("aria-disabled") !== "true" &&
                                    (
                                        label.includes("+") ||
                                        label.includes("increase") ||
                                        label.includes("increment")
                                    );
                            })
                            .sort((a, b) => {
                                const aRect = a.getBoundingClientRect();
                                const bRect = b.getBoundingClientRect();
                                return aRect.top - bRect.top || aRect.left - bRect.left;
                            });

                        for (const button of buttons) {
                            const before = getQuantity(button);
                            button.scrollIntoView({ block: "center" });
                            button.click();
                            setTimeout(() => {
                                done({
                                    clicked: true,
                                    before,
                                    after: getQuantity(button),
                                    label: textOf(button) || button.getAttribute("aria-label") || "increment",
                                });
                            }, 1000);
                            return;
                        }

                        done({ clicked: false });
                        """
                    )
                )
                if not clicked.get("clicked"):
                    raise Exception("No visible increment button was found")
                if (
                    clicked.get("before") is not None
                    and clicked.get("after") is not None
                    and clicked.get("after") <= clicked.get("before")
                ):
                    raise Exception(
                        "Increment click did not change quantity "
                        f"from {clicked.get('before')} to {clicked.get('after')}"
                    )

                clicked_count += 1
                self.logger.info(
                    "Increment button clicked (%s/%s). Quantity before: %s | after: %s",
                    clicked_count,
                    count,
                    clicked.get("before"),
                    clicked.get("after"),
                )
            except Exception as error:
                last_error = error
                self.logger.warning("Increment button click failed: %s", error)
                print(f"Increment button click failed: {error}")
                break

        if clicked_count == 0:
            if last_error and "did not change quantity" in str(last_error):
                self.logger.error("Increment button click did not update the quantity")
                raise Exception("Basket item quantity was not incremented") from last_error
            try:
                # Fallback for older basket markup that still exposes a plain plus button.
                self.logger.info("Using fallback increment locator")
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(SearchLocators.INCREMENT_BUTTON)
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element,
                )
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
                clicked_count = 1
            except Exception as error:
                self.logger.error("Failed to click Increment button")
                raise Exception("Failed to click Increment button") from (last_error or error)

        self.logger.info("Quantity incremented successfully for %s item(s)", clicked_count)
        print(f"Quantity incremented successfully for {clicked_count} item(s)")
        return clicked_count

    def click_checkout(self):
        self.logger.info("Clicking Checkout button")
        print("Clicking Checkout button...")
        for attempt in range(1, 4):
            try:
                # Prefer JS selection because sticky page layers can intercept normal Selenium clicks.
                clicked = self.driver.execute_script(
                    """
                    const buttons = [...document.querySelectorAll("button")]
                        .map((button) => {
                            const rect = button.getBoundingClientRect();
                            const text = (button.innerText || button.textContent || "").trim().toLowerCase();
                            return { button, rect, text };
                        })
                        .filter(({ button, rect, text }) =>
                            !button.disabled &&
                            button.getAttribute("aria-disabled") !== "true" &&
                            rect.width > 0 &&
                            rect.height > 0 &&
                            rect.bottom > 0 &&
                            rect.top < window.innerHeight &&
                            text.includes("checkout")
                        )
                        .sort((a, b) => a.rect.top - b.rect.top || a.rect.left - b.rect.left);

                    if (!buttons.length) return false;
                    buttons[0].button.click();
                    return true;
                    """
                )
                if clicked:
                    self.logger.info("Checkout button clicked")
                    print("Checkout button clicked")
                    time.sleep(2)
                    return
            except Exception as error:
                self.logger.warning("Checkout button click attempt %s failed: %s", attempt, error)
                print(f"Checkout button click attempt {attempt} failed: {error}")
            time.sleep(1)

        self.logger.error("Checkout button is not visible in the current viewport")
        raise Exception("Checkout button is not visible in the current viewport")

    def select_address(self):
        self.logger.info("Selecting saved delivery address")
        print("Selecting saved delivery address...")
        try:
            address = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(SearchLocators.ADDRESS_DIV)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", address)
            time.sleep(0.5)
            address.click()
            self.logger.info("Address selected successfully")
            print("Address selected successfully")
            time.sleep(2)
        except Exception as error:
            self.logger.warning("Address selection failed (may not be required): %s", error)
            print(f"Address selection failed (may not be required): {error}")

    def is_search_box_available(self, timeout=10):
        try:
            element = self.wait_for_search_box(timeout=timeout)
            return element.is_displayed()
        except TimeoutException:
            return False

    def is_add_button_available(self, timeout=15):
        try:
            return WebDriverWait(self.driver, timeout).until(
                lambda driver: self.driver.execute_script(
                    """
                    return [...document.querySelectorAll("button")].some((button) => {
                        const rect = button.getBoundingClientRect();
                        const text = (button.innerText || button.textContent || "").trim().toLowerCase();
                        return !button.disabled &&
                            button.getAttribute("aria-disabled") !== "true" &&
                            rect.width > 0 &&
                            rect.height > 0 &&
                            (text === "add" || text.includes("add"));
                    });
                    """
                )
            )
        except TimeoutException:
            return False

    def find_add_buttons(self):
        time.sleep(3)
        return self.driver.find_elements(*SearchLocators.ALL_ADD_BUTTONS)

    def is_checkout_available(self):
        try:
            self.wait_for_presence(SearchLocators.CHECKOUT_BUTTON, timeout=15)
            return True
        except TimeoutException:
            return False

    def is_basket_opened(self):
        try:
            self.wait_for_presence(SearchLocators.BASKET_CONTENT, timeout=15)
            return True
        except TimeoutException:
            return False

    def is_checkout_enabled(self):
        buttons = self.driver.find_elements(*SearchLocators.CHECKOUT_BUTTON)
        return bool(buttons) and buttons[0].is_enabled()

    def wait_for_checkout_page(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.url_contains("checkout"))
            return "checkout" in self.driver.current_url
        except TimeoutException:
            return False
