# -*- coding: utf-8 -*-
"""HTML Extraction Test: Archive GENERATED -> HTML extract with validation"""

from main_generator import FenokReportGenerator
from report_manager import ReportBatchManager
from datetime import datetime, timedelta
import os

print("="*60)
print("HTML Extraction Test")
print("="*60)

# Init
gen = FenokReportGenerator()

# Login
print("\n[Login]...")
if not gen._login_terminalx():
    print("[FAIL] Login failed")
    exit(1)
print("[OK] Login success")

# Setup
batch_manager = ReportBatchManager(gen.driver)
today = datetime.now()
report_date_str = today.strftime('%Y%m%d')
ref_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
ref_end = today.strftime('%Y-%m-%d')

# Add report
title = f"{report_date_str} HTML_TEST Part1"
batch_manager.add_report("Part1", title)
report = batch_manager.reports[0]
print(f"\nReport: {title}")

# Generate
print("\n[Generate]...")
if not gen.generate_report_html(report, report_date_str, ref_start, ref_end):
    print("[FAIL] Generate failed")
    gen.driver.quit()
    exit(1)
print(f"[OK] Generate OK: {report.url}")

# Monitor until GENERATED
print("\n[Monitor]...")
print("="*60)
success = batch_manager.monitor_and_retry()
print("="*60)

if not success or report.status != "GENERATED":
    print(f"[FAIL] Report status: {report.status}")
    gen.driver.quit()
    exit(1)

print(f"[OK] Report GENERATED: {report.url}")

# Extract HTML with validation
print("\n[Extract HTML]...")
output_path = os.path.join(gen.generated_html_dir, f"{report_date_str}_html_test.html")
if gen.extract_and_validate_html(report, output_path):
    print(f"[OK] HTML extracted: {output_path}")

    # Verify file exists
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"[OK] File exists: {file_size} bytes")

        # Check for supersearchx-body
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "supersearchx-body" in content:
                print("[OK] supersearchx-body found in HTML")
            else:
                print("[FAIL] supersearchx-body NOT found")
                gen.driver.quit()
                exit(1)

            if "No documents found" in content:
                print("[FAIL] 'No documents found' detected")
                gen.driver.quit()
                exit(1)
            else:
                print("[OK] No 'No documents found' error")

        print("\n[SUCCESS] HTML extraction test passed!")
        gen.driver.quit()
        exit(0)
    else:
        print(f"[FAIL] File not found: {output_path}")
        gen.driver.quit()
        exit(1)
else:
    print("[FAIL] HTML extraction failed")
    gen.driver.quit()
    exit(1)
