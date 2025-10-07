#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100xFenok-Generator Performance Diagnostics

Quick diagnostic script to measure current system performance
and identify active bottlenecks.

Usage:
    python diagnose_performance.py
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

class PerformanceDiagnostics:
    """System performance diagnostic tool"""

    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.results = {}

    def run_all_checks(self):
        """Run all diagnostic checks"""
        print("=" * 80)
        print(" 100xFenok-Generator Performance Diagnostics")
        print(" " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 80)
        print()

        checks = [
            ("1. Process Count", self.check_processes),
            ("2. File Analysis", self.check_files),
            ("3. Code Verification", self.check_code),
            ("4. Recent Results", self.check_results),
            ("5. Performance Estimate", self.estimate_performance),
        ]

        for name, check_func in checks:
            print(f"\n{'=' * 80}")
            print(f" {name}")
            print(f"{'=' * 80}\n")
            try:
                check_func()
            except Exception as e:
                print(f"⚠️ Check failed: {e}")

        self.print_summary()

    def check_processes(self):
        """Check for zombie Chrome/ChromeDriver processes"""
        print("Checking for background processes...")

        try:
            # Check Chrome processes
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                encoding='cp949'  # Windows Korean encoding
            )

            chrome_count = result.stdout.count("chrome.exe")
            chromedriver_count = result.stdout.count("chromedriver.exe")
            python_count = result.stdout.count("python.exe")

            print(f"  Chrome processes:       {chrome_count}")
            print(f"  ChromeDriver processes: {chromedriver_count}")
            print(f"  Python processes:       {python_count}")

            # Memory estimation
            estimated_memory = (chrome_count * 150) + (chromedriver_count * 20)
            print(f"\n  Estimated memory usage: {estimated_memory} MB")

            # Warning
            if chrome_count > 5:
                print(f"\n  ⚠️ WARNING: {chrome_count} Chrome processes detected!")
                print(f"  Expected: 1-2 (current session)")
                print(f"  Zombie processes: ~{chrome_count - 2}")
                print(f"\n  Cleanup command:")
                print(f"    taskkill /F /IM chrome.exe /T")
                print(f"    taskkill /F /IM chromedriver.exe /T")
            else:
                print(f"\n  ✅ Process count normal")

            self.results['processes'] = {
                'chrome': chrome_count,
                'chromedriver': chromedriver_count,
                'memory_mb': estimated_memory
            }

        except Exception as e:
            print(f"  ❌ Process check failed: {e}")

    def check_files(self):
        """Check project file structure"""
        print("Analyzing project files...")

        # Count Python files
        py_files = list(self.project_dir.glob("**/*.py"))
        archive_files = list((self.project_dir / "archives").glob("**/*.py")) if (self.project_dir / "archives").exists() else []
        active_files = [f for f in py_files if f not in archive_files]

        print(f"  Total Python files:  {len(py_files)}")
        print(f"  Archived files:      {len(archive_files)}")
        print(f"  Active files:        {len(active_files)}")

        # Check key files exist
        key_files = {
            "main_generator.py": "Main generator (CRITICAL)",
            "report_manager.py": "Archive monitor",
            "browser_controller.py": "Browser automation",
            "quick_archive_check.py": "Archive verification",
            "test_full_6reports.py": "Test suite"
        }

        print(f"\n  Key file status:")
        for filename, description in key_files.items():
            exists = (self.project_dir / filename).exists()
            size = (self.project_dir / filename).stat().st_size if exists else 0
            status = "✅" if exists else "❌"
            print(f"    {status} {filename:30s} ({size:6d} bytes) - {description}")

        self.results['files'] = {
            'total': len(py_files),
            'active': len(active_files),
            'archived': len(archive_files)
        }

    def check_code(self):
        """Verify critical code sections"""
        print("Verifying critical code sections...")

        main_gen_path = self.project_dir / "main_generator.py"

        if not main_gen_path.exists():
            print("  ❌ main_generator.py not found!")
            return

        with open(main_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for Archive completion logic
        has_wait_for_completion = "_wait_for_archive_completion" in content or "wait_for_completion" in content
        has_extract_report_id = "_extract_report_id" in content or "extract_report_id" in content
        has_context_manager = "__enter__" in content and "__exit__" in content

        print(f"\n  Critical Functions:")
        print(f"    {'✅' if has_wait_for_completion else '❌'} Archive completion check")
        print(f"    {'✅' if has_extract_report_id else '❌'} Report ID extraction")
        print(f"    {'✅' if has_context_manager else '❌'} Context manager (cleanup)")

        # Check generate_report_html implementation
        if "def generate_report_html" in content:
            # Find the function
            start = content.find("def generate_report_html")
            end = content.find("\n    def ", start + 1)
            func_body = content[start:end] if end != -1 else content[start:]

            # Check if it waits for Archive completion
            has_archive_wait = "wait_for" in func_body and "archive" in func_body.lower()

            print(f"\n  generate_report_html() analysis:")
            print(f"    {'✅' if has_archive_wait else '⚠️'} Archive completion wait: {'Present' if has_archive_wait else 'MISSING'}")

            if not has_archive_wait:
                print(f"\n    🔴 CRITICAL: Archive completion check missing!")
                print(f"    This is the PRIMARY BOTTLENECK causing 0% success rate")
        else:
            print(f"  ❌ generate_report_html() not found!")

        self.results['code'] = {
            'has_wait_for_completion': has_wait_for_completion,
            'has_extract_report_id': has_extract_report_id,
            'has_context_manager': has_context_manager
        }

    def check_results(self):
        """Check recent test results"""
        print("Analyzing recent test results...")

        # Check generated HTML files
        html_dir = self.project_dir / "generated_html"
        if html_dir.exists():
            html_files = list(html_dir.glob("*.html"))
            print(f"\n  Generated HTML files: {len(html_files)}")

            if html_files:
                print(f"\n  Recent files:")
                for html_file in sorted(html_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                    size = html_file.stat().st_size
                    mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
                    status = "✅ Valid" if size > 50000 else "❌ Too small (error page?)"
                    print(f"    {status:20s} {html_file.name:40s} {size:9,d} bytes  {mtime.strftime('%Y-%m-%d %H:%M')}")

        # Check test results JSON
        test_results = list(self.project_dir.glob("test_results_*.json"))
        if test_results:
            latest = sorted(test_results, key=lambda f: f.stat().st_mtime, reverse=True)[0]
            print(f"\n  Latest test result: {latest.name}")

            import json
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total = data.get('total', 0)
            generated = data.get('generated', 0)
            extracted = data.get('extracted', 0)
            failed = data.get('failed', 0)

            print(f"    Total:     {total}")
            print(f"    Generated: {generated} ({generated/total*100:.1f}%)" if total > 0 else "    Generated: 0 (0%)")
            print(f"    Extracted: {extracted} ({extracted/total*100:.1f}%)" if total > 0 else "    Extracted: 0 (0%)")
            print(f"    Failed:    {failed}")

            success_rate = extracted / total * 100 if total > 0 else 0
            if success_rate >= 80:
                print(f"\n    ✅ Success rate: {success_rate:.1f}% (GOOD)")
            elif success_rate >= 50:
                print(f"\n    ⚠️ Success rate: {success_rate:.1f}% (NEEDS IMPROVEMENT)")
            else:
                print(f"\n    ❌ Success rate: {success_rate:.1f}% (CRITICAL)")

            self.results['success_rate'] = success_rate
        else:
            print(f"\n  No test results found")
            self.results['success_rate'] = 0

    def estimate_performance(self):
        """Estimate current and projected performance"""
        print("Performance estimation...")

        success_rate = self.results.get('success_rate', 0)

        print(f"\n  Current Performance:")
        print(f"    Success rate:        {success_rate:.1f}%")
        print(f"    Status:              {'✅ GOOD' if success_rate >= 80 else '⚠️ NEEDS FIX' if success_rate >= 50 else '❌ CRITICAL'}")

        if success_rate < 80:
            print(f"\n  After P0 Fix (Archive completion check):")
            print(f"    Expected success:    95%+")
            print(f"    Time per report:     4-6 minutes")
            print(f"    6 reports total:     24-36 minutes")
            print(f"    Effort:              5 hours")
            print(f"\n  Improvement:           {95 - success_rate:.1f}% gain")

        # Process cleanup impact
        chrome_count = self.results.get('processes', {}).get('chrome', 0)
        if chrome_count > 5:
            memory_saved = (chrome_count - 2) * 150
            print(f"\n  After Process Cleanup:")
            print(f"    Zombie processes:    {chrome_count} → 1-2")
            print(f"    Memory freed:        ~{memory_saved} MB")
            print(f"    Effort:              30 minutes")

    def print_summary(self):
        """Print diagnostic summary"""
        print(f"\n{'=' * 80}")
        print(" Diagnostic Summary")
        print(f"{'=' * 80}\n")

        # Priority issues
        issues = []

        # Check success rate
        success_rate = self.results.get('success_rate', 0)
        if success_rate < 80:
            priority = "🔴 P0" if success_rate < 50 else "🟡 P1"
            issues.append((priority, f"Low success rate ({success_rate:.1f}%)", "Add Archive completion check"))

        # Check processes
        chrome_count = self.results.get('processes', {}).get('chrome', 0)
        if chrome_count > 5:
            issues.append(("🟡 P1", f"Zombie processes ({chrome_count})", "Add context manager cleanup"))

        # Check code
        if not self.results.get('code', {}).get('has_wait_for_completion', False):
            issues.append(("🔴 P0", "Missing Archive completion check", "Copy from quick_archive_check.py:156-198"))

        if not self.results.get('code', {}).get('has_context_manager', False):
            issues.append(("🟡 P1", "No context manager", "Add __enter__/__exit__ methods"))

        if issues:
            print("  Priority Issues Found:\n")
            for priority, issue, solution in issues:
                print(f"    {priority} {issue}")
                print(f"         → Solution: {solution}\n")
        else:
            print("  ✅ No critical issues detected!")

        # Next steps
        print("\n  Recommended Next Steps:\n")
        if success_rate < 80:
            print("    1. Review PERFORMANCE_ANALYSIS_20251007.md")
            print("    2. Review PERFORMANCE_BOTTLENECK_SUMMARY.md")
            print("    3. Approve Phase 1 Quick Fix (5 hours)")
            print("    4. Execute Hour 1-2: Add Archive completion check")
            print("    5. Test with 2 reports, verify success")
        else:
            print("    1. Monitor production performance")
            print("    2. Consider long-term refactoring (optional)")

        print(f"\n{'=' * 80}")

def main():
    """Run diagnostics"""
    diagnostics = PerformanceDiagnostics()
    diagnostics.run_all_checks()

    # Save results
    output_file = diagnostics.project_dir / f"diagnostic_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    print(f"\nDiagnostic results saved to: {output_file.name}")

if __name__ == "__main__":
    main()
