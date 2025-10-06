# -*- coding: utf-8 -*-
"""Quick test: report_manager.py Archive wait logic"""

from main_generator import FenokReportGenerator
from report_manager import ReportBatchManager
from datetime import datetime, timedelta

print("="*60)
print("Quick Test: Single Report Generation")
print("="*60)

# Init
gen = FenokReportGenerator()

# Login
print("\n[Login]...")
if not gen._login_terminalx():
    print("Login FAILED")
    exit(1)
print("Login OK")

# Setup
batch_manager = ReportBatchManager(gen.driver)
today = datetime.now()
report_date_str = today.strftime('%Y%m%d')
ref_start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
ref_end = today.strftime('%Y-%m-%d')

# Add report
title = f"{report_date_str} TEST Part1"
batch_manager.add_report("Part1", title)
report = batch_manager.reports[0]
print(f"\nReport: {title}")

# Generate
print("\n[Generate]...")
if not gen.generate_report_html(report, report_date_str, ref_start, ref_end):
    print("Generate FAILED")
    gen.driver.quit()
    exit(1)
print(f"Generate OK: {report.url}")

# Monitor
print("\n[Monitor]...")
print("="*60)
success = batch_manager.monitor_and_retry()
print("="*60)

# Result
print(f"\nStatus: {report.status}")
if report.status == "GENERATED":
    print("\n[SUCCESS] Report is GENERATED!")
    gen.driver.quit()
    exit(0)
else:
    print(f"\n[FAIL] Report status: {report.status}")
    gen.driver.quit()
    exit(1)
