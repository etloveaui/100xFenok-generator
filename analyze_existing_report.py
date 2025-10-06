# -*- coding: utf-8 -*-
"""Analyze existing GENERATED report from Archive"""

from main_generator import FenokReportGenerator
import time

print("="*60)
print("Analyze Existing GENERATED Report")
print("="*60)

# Init
gen = FenokReportGenerator()

# Login
print("\n[Login]...")
if not gen._login_terminalx():
    print("[FAIL] Login failed")
    exit(1)
print("[OK] Login success")

# Go to Archive
print("\n[Archive]...")
gen.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
time.sleep(5)

# JavaScript rendering wait
print("JavaScript rendering wait...")
time.sleep(7)

# Find first GENERATED report
from selenium.webdriver.common.by import By
rows = gen.driver.find_elements(By.XPATH, "//table/tbody/tr")
print(f"Found {len(rows)} rows in Archive")

generated_url = None
generated_title = None

for row in rows:
    try:
        title_elem = row.find_element(By.XPATH, ".//td[1]")
        status_elem = row.find_element(By.XPATH, ".//td[4]")

        title = title_elem.text.strip()
        status = status_elem.text.strip()

        if status.upper() == "GENERATED":
            # Get URL from title link
            link = title_elem.find_element(By.XPATH, ".//a")
            generated_url = link.get_attribute("href")
            generated_title = title
            print(f"\n[FOUND] GENERATED report:")
            print(f"  Title: {title}")
            print(f"  URL: {generated_url}")
            break
    except:
        continue

if not generated_url:
    print("[FAIL] No GENERATED report found in Archive")
    gen.driver.quit()
    exit(1)

# Test 1: Visit GENERATING report (if exists)
print("\n" + "="*60)
print("TEST 1: GENERATING Report HTML Analysis")
print("="*60)

generating_url = None
for row in rows:
    try:
        title_elem = row.find_element(By.XPATH, ".//td[1]")
        status_elem = row.find_element(By.XPATH, ".//td[4]")
        status = status_elem.text.strip()

        if status.upper() == "GENERATING":
            link = title_elem.find_element(By.XPATH, ".//a")
            generating_url = link.get_attribute("href")
            generating_title = title_elem.text.strip()
            print(f"Found GENERATING report: {generating_title}")
            print(f"URL: {generating_url}")
            break
    except:
        continue

if generating_url:
    gen.driver.get(generating_url)
    time.sleep(5)
    html = gen.driver.page_source

    print("\nGENERATING Report HTML Checks:")
    print(f"  - Has 'Generating your report': {'YES' if 'Generating your report' in html else 'NO'}")
    print(f"  - Has 'it may take up to 5 minutes': {'YES' if 'it may take up to 5 minutes' in html else 'NO'}")
    print(f"  - Has 'supersearchx-body': {'YES' if 'supersearchx-body' in html else 'NO'}")
    print(f"  - Has 'No documents found': {'YES' if 'No documents found' in html else 'NO'}")
else:
    print("No GENERATING report found. Skipping TEST 1.")

# Test 2: Visit GENERATED report
print("\n" + "="*60)
print("TEST 2: GENERATED Report HTML Analysis")
print("="*60)

gen.driver.get(generated_url)
print(f"Visiting: {generated_url}")
print("Waiting 10 seconds for page load...")
time.sleep(10)

html = gen.driver.page_source

print("\nGENERATED Report HTML Checks:")
print(f"  - Has 'Generating your report': {'YES' if 'Generating your report' in html else 'NO'}")
print(f"  - Has 'it may take up to 5 minutes': {'YES' if 'it may take up to 5 minutes' in html else 'NO'}")
print(f"  - Has 'supersearchx-body': {'YES' if 'supersearchx-body' in html else 'NO'}")
print(f"  - Has 'No documents found': {'YES' if 'No documents found' in html else 'NO'}")
print(f"  - HTML length: {len(html)} chars")

# Try WebDriverWait for supersearchx-body
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

print("\nWaiting for supersearchx-body (30s timeout)...")
try:
    WebDriverWait(gen.driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "supersearchx-body"))
    )
    print("[SUCCESS] supersearchx-body found!")

    # Save HTML
    import os
    output_path = os.path.join(gen.generated_html_dir, "test_generated_report.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(gen.driver.page_source)
    print(f"[OK] HTML saved: {output_path}")

except TimeoutException:
    print("[FAIL] supersearchx-body NOT found after 30s")

    # Save HTML anyway for analysis
    import os
    output_path = os.path.join(gen.generated_html_dir, "test_failed_report.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(gen.driver.page_source)
    print(f"[DEBUG] HTML saved for analysis: {output_path}")

print("\n[DONE] Analysis complete")
gen.driver.quit()
