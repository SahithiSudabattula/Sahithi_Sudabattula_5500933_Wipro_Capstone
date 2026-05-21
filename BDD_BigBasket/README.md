# BigBasket BDD Automation Project

This project converts the completed Selenium + pytest BigBasket automation into a BDD framework using Behave.

## Test coverage

- BigBasket login flow with manual OTP verification
- Product search and add to basket
- Search, add, basket, quantity increment, and checkout navigation
- Invalid product search negative scenario
- Empty basket checkout negative scenario

## Project structure

```text
features/         BDD feature files and step definitions
locators/         Selenium locators grouped by page/functionality
pages/            Page object classes that use locators
utils/            Config, logging, and screenshot helpers
reports/          Allure results and generated report
screenshots/      Failure and passed negative scenario screenshots
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests

Run all scenarios:

```powershell
behave
```

By default, `behave` shows normal terminal output and also generates Allure result files in:

```text
reports/allure-results
```

Run selected tags:

```powershell
behave --tags=@smoke
behave --tags=@negative
behave --tags=@checkout
```

Open the Allure report:

If the Allure command-line tool is installed, `behave` also generates:

```text
reports/allure-report/index.html
reports/report.html
```

Open the report in a local server:

```powershell
allure serve reports/allure-results
```

If `allure` is not recognized, install the Allure command-line tool or open the generated `reports/allure-results` folder from an IDE/plugin that supports Allure.

Important: BigBasket login requires OTP. When the browser reaches the OTP screen, enter the OTP manually. The automation waits for the Verify button and continues after verification.
