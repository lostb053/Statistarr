# MIT License
# Copyright (c) 2025 LostB053
# See LICENSE file in the project root for full license text.

import time
start_time = time.time()


import os
import re
import json
import requests

# Configuration
if not "config.json" in os.listdir():
    raise Exception("No config file found")

with open("config.json", "r") as config_file:
    config = json.load(config_file)
APPS = config["Statistarr"]

# --- Functions ---
last_date = ""
old_stats = {}
if any((f.endswith(".json") and f.startswith("Stats ")) for f in os.listdir()):
    matches = [f for f in os.listdir() if (f.endswith(".json") and f.startswith("Stats "))]
    last_date = re.sub(r"Stats (.*)\.json", r"\1", matches[0]).replace("_",":")
    with open(matches[0], "r") as file:
        old_stats = json.load(file)
    os.remove(matches[0])

def fetch_all_logs(app):
    page = 1
    all_logs = []
    try:
        while True:
            r = requests.get(f"{app['url']}/api/v3/history?page={page}&pageSize=1000&eventType=4&eventType=1&sortKey=date&sortDirection=descending", headers={"X-Api-Key": app['api_key']})
            if r.status_code != 200:
                print(f"Failed to fetch logs from {app['name']}: {r.status_code}")
                break
            page_logs = r.json().get('records')
            if not page_logs or page_logs == []:
                break
            if not max(last_date, page_logs[0]['date']) == page_logs[0]['date']:
                break
            all_logs.extend(page_logs)
            page += 1
        return all_logs
    except:
        print(f"Can't connect to {app['name']}")
        return []

date_ = []

def parse_logs(app_name, logs):
    new_records = 0
    stats = {}
    if app_name in old_stats.keys():
        stats = old_stats[app_name]
    if logs == [] or logs is None:
        return stats
    raw_stats = {}
    date_.append(logs[0]['date'])
    for log in logs:
        if (last_date == log['date']) or (max(last_date, log['date']) == last_date):
            break
        if log.get('downloadId') not in raw_stats.keys():
            raw_stats[log.get('downloadId')] = {}
        data = raw_stats[log.get('downloadId')]
        if log['eventType'] == "downloadFailed":
            if log['data']['message'] != "Unpacking failed, disk full":
                data['failed'] = True
        if log['eventType'] == "grabbed":
            data['indexer'] = log['data']['indexer']
    for key in raw_stats.keys():
        new_records += 1
        unit = raw_stats[key]
        if unit['indexer'] in stats.keys():
            if 'failed' in unit.keys():
                stats[unit['indexer']]['fail'] += 1
            else:
                stats[unit['indexer']]['success'] += 1
        else:
            if 'failed' in unit.keys():
                stats[unit['indexer']] = {"success": 0, "fail": 1}
            else:
                stats[unit['indexer']] = {"success": 1, "fail": 0}
    print(f"\n{new_records} New records found from {app_name}")
    return stats

def merge_stats(all_stats):
    merged = {}
    for stats in all_stats.values():
        for indexer, counts in stats.items():
            if indexer not in merged:
                merged[indexer] = {'success': 0, 'fail': 0}
            merged[indexer]['success'] += counts['success']
            merged[indexer]['fail'] += counts['fail']
    return merged

def backup(stats: dict):
    filename = "Stats " + max(date_).replace(":","_") + ".json"
    with open(filename, "w") as file:
        json.dump(stats, file)

# --- Main ---

all_app_stats = {}
app_logs = {}

for app in APPS:
    print(f"Fetching logs from {app['name']}...")
    logs = fetch_all_logs(app)
    app_logs[app['name']] = logs

# Two loops cuz parsing a long log list may take time, so to get all logs as close as possible to the final saved date

for app in app_logs.keys():
    app_stats = parse_logs(app, app_logs[app])
    all_app_stats[app] = app_stats
    print(f"\n== {app} ==")
    for indexer, counts in app_stats.items():
        print(f"- {indexer}: {counts['success']} successes, {counts['fail']} failures")

backup(all_app_stats)

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


end_time = time.time()    # Record end time
elapsed_time = end_time - start_time
print(f"\nTime taken: {elapsed_time:.2f} seconds")


input("\nPress Enter to exit...")
