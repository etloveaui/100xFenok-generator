"""
Updated automation script for 100xFenok Daily Wrap generation.

This script improves robustness around navigation, selectors and
status polling based on a recent root‑cause analysis.  It is not
fully functional without proper environment setup (Selenium
WebDriver, credentials, etc.), but illustrates the key
modifications required to unblock the pipeline.

Key improvements:

1. **Navigation Guard** – after attempting to load the report form
   URL, verify that we have actually landed on a form page by
   checking for the presence of expected input fields.  If we are
   redirected back to the archive/dashboard, the script will
   attempt a fallback navigation via the "Create Custom Report"
   button.  If navigation still fails, an exception is raised.

2. **Dynamic Column Detection** – when scanning the archive table
   for generated/failed status, the script now uses table header
   text to determine the index of the "Report Name" and "Status"
   columns, rather than assuming fixed positions.  This makes the
   polling logic resilient to future UI changes.

3. **File Upload Loop** – for any file upload fields (e.g. sample
   report or sources), send keys one at a time to ensure all files
   are uploaded.  Some input elements ignore newline‑separated
   paths, so this loop approach improves reliability.

4. **Logging and Debugging Hooks** – additional print statements
   record the current URL, presence/absence of expected elements
   and any redirect behaviour.  These logs make it easier to
   understand why form entry might fail in headless runs.

To use this script you must provide valid TerminalX credentials
via environment variables or another secrets mechanism.  Selenium
and chromedriver must also be installed in your environment.
"""

import os
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


LOGIN_URL = "https://theterminalx.com/agent/enterprise"
REPORT_FORM_URL = "https://theterminalx.com/agent/enterprise/report/form/10"
ARCHIVE_URL = "https://theterminalx.com/agent/enterprise/report/archive"


class FenokDailyWrap:
    def __init__(self, username: str, password: str, driver: webdriver.Chrome):
        self.username = username
        self.password = password
        self.driver = driver

    def login(self) -> None:
        """Log into TerminalX using provided credentials."""
        self.driver.get(LOGIN_URL)
        # wait for the login button on landing page
        try:
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_btn.click()
        except TimeoutException:
            pass  # maybe already on login form
        # fill credentials
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your email']"))
        )
        pw_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
        email_input.clear(); email_input.send_keys(self.username)
        pw_input.clear(); pw_input.send_keys(self.password)
        # submit
        submit = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")
        submit.click()
        # wait for sidebar to appear indicating login success
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='sidebar']"))
        )

    def navigate_to_form(self) -> None:
        """Ensure we land on the custom report form.  Try direct URL and fallback."""
        self.driver.get(REPORT_FORM_URL)
        time.sleep(2)  # allow potential redirect
        current = self.driver.current_url
        print(f"Navigated to {current}")
        # Check for input field presence
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder and contains(@placeholder, 'topic')]") )
            )
            print("Form detected via direct URL")
            return
        except TimeoutException:
            print("Form not detected, attempting fallback navigation via UI")
        # fallback: open AI Report Builder and click +Create Custom Report
        self.driver.get("https://theterminalx.com/agent/enterprise/report")
        try:
            create_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Create Custom Report')]"))
            )
            create_btn.click()
        except TimeoutException:
            raise RuntimeError("Failed to locate Create Custom Report button")
        # wait again for form fields
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder and contains(@placeholder, 'topic')]") )
            )
            print("Form detected via fallback navigation")
        except TimeoutException:
            raise RuntimeError("Unable to load report form after fallback navigation")

    def upload_files(self, input_xpath: str, paths: list[str]) -> None:
        """Upload multiple files by sending keys one at a time."""
        file_input = self.driver.find_element(By.XPATH, input_xpath)
        for path in paths:
            file_input.send_keys(path)
            time.sleep(1)  # slight delay to ensure each file registers

    def determine_archive_columns(self) -> tuple[int, int]:
        """Determine column indices for report name and status dynamically."""
        header_cells = self.driver.find_elements(By.XPATH, "//table/thead/tr/th")
        name_idx = status_idx = None
        for idx, cell in enumerate(header_cells, start=1):
            text = cell.text.strip().lower()
            if 'report' in text or 'name' in text:
                name_idx = idx
            if 'status' in text:
                status_idx = idx
        if name_idx is None or status_idx is None:
            raise RuntimeError("Could not determine archive column indices")
        print(f"Archive columns detected: name={name_idx}, status={status_idx}")
        return name_idx, status_idx

    # Additional methods would follow to complete the runbook logic (e.g. part
    # generation loop, polling, HTML extraction).  These would incorporate the
    # dynamic selectors and guard clauses added above.


def main():
    # Example usage – this entry point will not run within this environment
    # because it relies on a full Selenium/Chromedriver setup.  Provided for
    # completeness only.
    username = os.environ.get('TERMINALX_USER')
    password = os.environ.get('TERMINALX_PASS')
    if not username or not password:
        raise SystemExit("Please set TERMINALX_USER and TERMINALX_PASS environment variables")
    driver = webdriver.Chrome()
    gen = FenokDailyWrap(username, password, driver)
    try:
        gen.login()
        gen.navigate_to_form()
        # further logic goes here
    finally:
        driver.quit()


if __name__ == '__main__':
    main()