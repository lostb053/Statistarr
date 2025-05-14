# MIT License
# Copyright (c) 2025 LostB053
# See LICENSE file in the project root for full license text.

import os
import re
import time
import json
import shutil
import requests
from datetime import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration
if not "config.json" in os.listdir():
    raise Exception("No config file found")


with open("config.json", "r") as config_file:
    config = json.load(config_file)
APPS: list = config["Statistarr"]
if APPS == []:
    raise Exception("No apps found in config file")


# --- Functions ---
date_ = []
untracked_download_id = []

def backup(filename):
    if not os.path.exists("backup"):
        os.mkdir("backup")
        shutil.copy(filename, "backup")
    else:
        files = os.listdir("backup")
        latest_file = max(files)
        if filename == latest_file:
            return
        date_ts = dt.fromisoformat(re.sub(r"Stats (.*)\.json", r"\1", latest_file).replace("_",":")).timestamp()
        if dt.now().timestamp() - date_ts > 21000:
            shutil.copy(filename, "backup")


def fetch_old_stats() -> list[str, dict]:
    matches = [f for f in os.listdir() if f.endswith(".json") and f.startswith("Stats ")]
    if matches and len(matches) == 1:
        last_date = re.sub(r"Stats (.*)\.json", r"\1", matches[0]).replace("_",":")
        with open(matches[0], "r") as file:
            old_stats = json.load(file)
        backup(matches[0])
        os.remove(matches[0])
    else:
        if "backup" in os.listdir():
            files = os.listdir("backup")
            latest_file = os.path.join("backup", max(files))
            with open(latest_file, "r") as file:
                old_stats = json.load(file)
            last_date = re.sub(r"Stats (.*)\.json", r"\1", latest_file).replace("_",":")
    return last_date, old_stats


def fetch_all_logs(app, last_date: str = "") -> list:
    page = 1
    all_logs = []
    try:
        while True:
            r = requests.get(f"{app['url']}/api/v3/history?page={page}&pageSize=1000&eventType=4&eventType=1&sortKey=date&sortDirection=descending", headers={"X-Api-Key": app['api_key']})
            if r.status_code != 200:
                with open("connection_failure.log", "a") as file:
                    file.write(f"=============================================\n"+
                               f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')} - {r.status_code} - {app['name']}\n\n")
                break
            page_logs = r.json().get('records')
            if not page_logs or page_logs == []:
                break
            if not last_date <= page_logs[0]['date']:
                break
            all_logs.extend(page_logs)
            page += 1
        return all_logs
    except Exception as e:
        with open("error.log", "a") as file:
            file.write(f"=============================================\n"+
                       f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')} - {e}\n\n"+
                       f"{last_date}\n\n{app['name']}\n\n{all_logs}\n\n\n\n\n")


def parse_logs(app_name, logs, last_date: str = "", old_stats: dict = {}):
    new_records = 0
    stats = {}
    if app_name in old_stats.keys():
        stats = old_stats[app_name]
    if logs == [] or logs is None:
        return stats
    raw_stats = {}
    date_.append(logs[0]['date'])
    for log in logs:
        if (last_date >= log['date']):
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
        if not 'indexer' in unit.keys():
            untracked_download_id.append(key)
        elif unit['indexer'] in stats.keys():
            if 'failed' in unit.keys():
                stats[unit['indexer']]['fail'] += 1
            else:
                stats[unit['indexer']]['success'] += 1
        else:
            if 'failed' in unit.keys():
                stats[unit['indexer']] = {"success": 0, "fail": 1}
            else:
                stats[unit['indexer']] = {"success": 1, "fail": 0}
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


def json_dump(stats: dict):
    try:
        filename = "Stats " + max(date_).replace(":","_") + ".json"
        with open(filename, "w") as file:
            json.dump(stats, file)
        date_.clear()
    except:
        if "backup" in os.listdir():
            files = os.listdir("backup")
            latest_file = os.path.join("backup", max(files))
            shutil.copy(latest_file, "./")


def fix_untracked(app, stats):
    if untracked_download_id == []:
        return
    failed_fixes = 0
    for i in untracked_download_id:
        r = requests.get(f"{app['url']}/api/v3/history?page=1&pageSize=1000&eventType=1&downloadId={i}", headers={"X-Api-Key": app['api_key']})
        page_logs = r.json().get('records')
        try:
            indexer_ = page_logs[0]['data']['indexer']
            stats[indexer_]["success"] -= 1
            stats[indexer_]["fail"] += 1
        except:
            failed_fixes += 1
            with open("untracked.log", "a") as file:
                file.write(f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')} - {app['name']} - {i}\n")
    untracked_download_id.clear()


# --- Main ---
def statistarr():
    try:
        all_app_stats = {}
        app_logs = {}
        last_date, old_stats = fetch_old_stats()
        for app in APPS:
            logs = fetch_all_logs(app, last_date)
            app_logs[app['name']] = logs
        # Two loops cuz parsing a long log list may take time, so to get all logs as close as possible to the final saved date
        for app in app_logs.keys():
            app_stats = parse_logs(app, app_logs[app], last_date, old_stats)
            fix_untracked([i for i in APPS if i['name']==app][0], app_stats)
            all_app_stats[app] = app_stats
        json_dump(all_app_stats)
    except Exception as e:
        with open("error.log", "a") as file:
            file.write(f"=============================================\n"+
                       f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')} - {e}\n\n"+
                       f"{last_date}\n\n{old_stats}\n\n{app_logs}\n\n\n\n\n")


statistarr()

scheduler = BackgroundScheduler()
scheduler.add_job(statistarr, 'interval', hours=1)
scheduler.start()


try:
    while True:
        time.sleep(1)  # Keeps script alive
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()