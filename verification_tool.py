"""
verification_tool.py
Phase 4: Generate a verification sample, apply corrections, and calculate accuracy.
"""

import json
import csv
import os
from datetime import datetime
from collections import defaultdict

# ---------- CONFIG ----------
INPUT_JSON = "output/pass_1.json"
APPS_JSON = "data/apps.json"
OUTPUT_SAMPLE_CSV = "verification_sample.csv"
OUTPUT_SAMPLE_JSON = "verification_sample.json"
OUTPUT_PASS_2 = "output/pass_2.json"

def flatten_row(row):
    """Converts lists to strings for CSV."""
    flat = row.copy()
    # Convert auth_methods list to a comma-separated string
    if isinstance(flat.get("auth_methods"), list):
        flat["auth_methods"] = ",".join(flat["auth_methods"])
    # Ensure all required fields exist for manual editing
    flat["manual_auth_methods"] = ""
    flat["manual_self_serve"] = ""
    flat["manual_api_surface"] = ""
    flat["manual_buildability"] = ""
    flat["manual_blocker"] = ""
    return flat

def unflatten_row(flat):
    """Converts strings back to lists for JSON."""
    row = flat.copy()
    # Split auth_methods back into a list
    if isinstance(row.get("auth_methods"), str) and row["auth_methods"]:
        row["auth_methods"] = [m.strip() for m in row["auth_methods"].split(",") if m.strip()]
    return row

def generate_sample():
    print("📂 Loading data...")
    with open(APPS_JSON, "r") as f:
        all_apps = json.load(f)
    with open(INPUT_JSON, "r") as f:
        pass_1 = json.load(f)

    # Create a lookup for the pass_1 data by app_id
    pass_1_lookup = {app["app_id"]: app for app in pass_1}

    # Group apps by category
    categories = defaultdict(list)
    for app in all_apps:
        categories[app["category"]].append(app["app_id"])

    # Select up to 2 apps per category
    selected_ids = []
    for cat, ids in categories.items():
        # Take the first 2 (if less than 2, take all)
        selected_ids.extend(ids[:2])

    # Build the sample data
    sample_data = []
    for app_id in selected_ids:
        if app_id in pass_1_lookup:
            sample_data.append(pass_1_lookup[app_id])

    print(f"✅ Selected {len(sample_data)} apps for verification.")

    # Save as JSON (for reference)
    with open(OUTPUT_SAMPLE_JSON, "w") as f:
        json.dump(sample_data, f, indent=2)

    # Save as CSV (for easy editing)
    with open(OUTPUT_SAMPLE_CSV, "w", newline="", encoding="utf-8") as f:
        if not sample_data:
            return
        
        # Flatten the first row to get headers
        flat_sample = [flatten_row(row) for row in sample_data]
        fieldnames = list(flat_sample[0].keys())
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_sample)

    print(f"📄 Sample saved to: {OUTPUT_SAMPLE_CSV}")
    print("👉 Open this file in Excel or Google Sheets.")
    print("👉 Look for the columns that start with 'manual_'. Fill them in based on real docs.")
    print("   - manual_auth_methods: e.g., 'oauth2' or 'oauth2,api_key'")
    print("   - manual_self_serve: 'true' or 'false'")
    print("   - manual_api_surface: 'rest', 'graphql', etc.")
    print("   - manual_buildability: 'yes', 'partial', or 'no'")
    print("   - manual_blocker: write the blocker, or leave empty if buildability is 'yes'")
    print("\n💡 Tip: Use the 'website_hint' column to find the docs!")

def apply_verification():
    print("📂 Loading pass_1 and your corrections...")
    
    with open(INPUT_JSON, "r") as f:
        pass_1 = json.load(f)
    
    corrected_rows = []
    with open(OUTPUT_SAMPLE_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            corrected_rows.append(row)

    # Build a lookup for corrections by app_id
    corrections = {}
    for row in corrected_rows:
        app_id = int(row["app_id"])
        corrections[app_id] = row

    pass_2 = []
    total_corrected = 0
    stats = {"auth": 0, "self_serve": 0, "api_surface": 0, "buildability": 0}
    total_checked = len(corrections)

    for app in pass_1:
        app_id = app["app_id"]
        if app_id in corrections:
            corr = corrections[app_id]
            # Check if the user actually filled in manual fields
            manual_auth = corr.get("manual_auth_methods", "").strip()
            manual_self = corr.get("manual_self_serve", "").strip().lower()
            manual_api = corr.get("manual_api_surface", "").strip()
            manual_build = corr.get("manual_buildability", "").strip()
            manual_block = corr.get("manual_blocker", "").strip()

            # Count accuracy: compare original vs manual
            if manual_auth:
                # Compare as sets to handle different orders
                orig_auth = set(app["auth_methods"])
                new_auth = set([x.strip() for x in manual_auth.split(",") if x.strip()])
                if orig_auth == new_auth:
                    stats["auth"] += 1
                # Apply correction
                app["auth_methods"] = list(new_auth)

            if manual_self in ["true", "false"]:
                new_self = manual_self == "true"
                if app["self_serve"] == new_self:
                    stats["self_serve"] += 1
                app["self_serve"] = new_self
                # Update the basis to show it was verified
                app["self_serve_basis"] = f"Manually verified: {app['self_serve_basis']}"

            if manual_api:
                if app["api_surface"] == manual_api:
                    stats["api_surface"] += 1
                app["api_surface"] = manual_api

            if manual_build in ["yes", "partial", "no"]:
                if app["buildability_verdict"] == manual_build:
                    stats["buildability"] += 1
                app["buildability_verdict"] = manual_build
                if manual_block:
                    app["blocker"] = manual_block
                elif manual_build == "yes":
                    app["blocker"] = None

            # Mark as verified
            app["verified"] = True
            app["verification_note"] = f"Verified on {datetime.now().strftime('%Y-%m-%d')}"
            total_corrected += 1

        pass_2.append(app)

    # Save pass_2
    with open(OUTPUT_PASS_2, "w") as f:
        json.dump(pass_2, f, indent=2)

    print(f"\n✅ Done! {total_corrected} apps corrected.")
    print(f"📄 Saved to: {OUTPUT_PASS_2}")

    # Print Accuracy Report
    print("\n" + "="*50)
    print("📊 VERIFICATION ACCURACY REPORT")
    print("="*50)
    print(f"Sample Size: {total_checked} apps")
    if total_checked > 0:
        print(f"Auth Method correct: {stats['auth']}/{total_checked} ({round(stats['auth']/total_checked*100, 1)}%)")
        print(f"Self-Serve correct: {stats['self_serve']}/{total_checked} ({round(stats['self_serve']/total_checked*100, 1)}%)")
        print(f"API Surface correct: {stats['api_surface']}/{total_checked} ({round(stats['api_surface']/total_checked*100, 1)}%)")
        print(f"Buildability correct: {stats['buildability']}/{total_checked} ({round(stats['buildability']/total_checked*100, 1)}%)")
        
        # Calculate overall average
        total_correct = stats['auth'] + stats['self_serve'] + stats['api_surface'] + stats['buildability']
        total_possible = total_checked * 4
        avg = round(total_correct / total_possible * 100, 1)
        print("-"*50)
        print(f"📈 OVERALL ACCURACY (Pass 1): {avg}%")
        print("="*50)
        print("💡 If you corrected a lot of mistakes, your Pass 2 accuracy is now ~100% for these fields.")
        print("   In your HTML report, use the Pass 1 vs Pass 2 comparison!")

if __name__ == "__main__":
    print("1️⃣  Generate verification sample? (type 'generate')")
    print("2️⃣  Apply corrections and create pass_2? (type 'apply')")
    choice = input("Enter command: ").strip().lower()
    
    if choice == "generate":
        generate_sample()
    elif choice == "apply":
        apply_verification()
    else:
        print("Invalid choice. Please run with 'generate' or 'apply'.")