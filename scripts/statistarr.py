# MIT License
# Copyright (c) 2025 LostB053
# See LICENSE file in the project root for full license text.

import os
import json

# --- Functions ---

if any((f.endswith(".json") and f.startswith("Stats ")) for f in os.listdir()):
    matches = [f for f in os.listdir() if (f.endswith(".json") and f.startswith("Stats "))]
    with open(matches[0], "r") as file:
        all_app_stats: dict = json.load(file)
else:
    raise Exception("No previous stats found.")


def merge_stats(all_stats: dict):
    merged = {}
    for stats in all_stats.values():
        for indexer, counts in stats.items():
            if indexer not in merged:
                merged[indexer] = {'success': 0, 'fail': 0}
            merged[indexer]['success'] += counts['success']
            merged[indexer]['fail'] += counts['fail']
    return merged

# --- Main ---

for app in all_app_stats.keys():
    app_stats: dict = all_app_stats[app]
    print(f"\n== {app} ==")
    for indexer, counts in app_stats.items():
        print(f"- {indexer}: {counts['success']} successes, {counts['fail']} failures")

# Final combined stats
print("\n== TOTAL ==")
combined_stats = merge_stats(all_app_stats)

total_success = sum(counts['success'] for counts in combined_stats.values())
total_fail = sum(counts['fail'] for counts in combined_stats.values())
total_grabs = total_success + total_fail

print(f"Total Grabs: {total_grabs}")
print(f"Total Successes: {total_success}")
print(f"Total Failures: {total_fail}\n")

for indexer, counts in sorted(combined_stats.items(), key=lambda x: (-x[1]['fail'], x[0])):
    indexer_success = counts['success']
    indexer_fail = counts['fail']
    indexer_total = indexer_success + indexer_fail
    
    success_percent = (indexer_success / total_success * 100) if total_success else 0
    fail_percent = (indexer_fail / total_fail * 100) if total_fail else 0
    failure_rate = (indexer_fail / indexer_total * 100) if indexer_total else 0

    # Failure rate color
    if failure_rate > 20:
        fail_color = '\033[91m'  # Red for high failure rates
    else:
        fail_color = '\033[92m'  # Green for low failure rates

    # Print with failure rate color
    print(f"- {indexer}: {indexer_success} successes ({success_percent:.1f}%), "
          f"{indexer_fail} failures ({fail_percent:.1f}%), "
          f"{fail_color}{failure_rate:.1f}% Failure Rate\033[0m")


input("\nPress Enter to exit...")