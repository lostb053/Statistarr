import os
import json
from quickchart import QuickChart
from plyer import notification
from math import floor

qc = QuickChart()
qc.width = 1000
qc.height = 600
qc.version = '2'


def send_error_notification(error = "Chart error", message = "No JSON dump found. Run statistarr script first"):
    notification.notify(
        title=f'Statistarr: {error}',
        message=message,
        timeout=10  # seconds
    )


with open("config.json", "r") as config_file:
    config = json.load(config_file)
config_dict = config["Quickchart"]

for key, value in config_dict.items():
    if key != "redacted":
        setattr(qc, key, value)
    if key == "redacted":
        redacted_ = value


# Your raw JSON data
if any((f.endswith(".json") and f.startswith("Stats ")) for f in os.listdir()):
    matches = [f for f in os.listdir() if (f.endswith(".json") and f.startswith("Stats "))]
    with open(matches[0], "r") as file:
        raw_data = json.load(file)
else:
    send_error_notification()
    raise Exception("No JSON dump found. Run statistarr script first, or retry after a few minutes if the script is already running.")


# 1. Combine totals per indexer
totals = {}
for app, indexers in raw_data.items():
    for indexer, stats in indexers.items():
        short_name = indexer.split(" (")[0]  # Remove (Prowlarr)
        if short_name not in totals:
            totals[short_name] = {"success": 0, "fail": 0}
        totals[short_name]["success"] += stats.get("success", 0)
        totals[short_name]["fail"] += stats.get("fail", 0)


# 2. Prepare labels and data arrays
sorted_totals = sorted(totals.items(), key=lambda x: x[1]["success"], reverse=True)
labels = []
success_data = []
fail_data = []
failure_rates = []  # for datalabels plugin


for indexer, stats in sorted_totals:
    labels.append(indexer)
    success_data.append(stats["success"])
    fail_data.append(stats["fail"])
    total = stats["success"] + stats["fail"]
    if total > 0:
        failure_rates.append(str(round(stats["fail"]/total*100, 1))+"%")
    else:
        failure_rates.append("0.0%")
failure_rates_json = json.dumps(failure_rates)


lower_labels = [label.lower() for label in labels]
for i in redacted_:
    labels[lower_labels.index(i)] = "REDACTED"


# 3. Build chart config
qc.config = f"""{{
    "type": "bar",
    "data": {{
        "labels": {labels},
        "datasets": [
            {{
                "label": "Success",
                "data": {success_data},
                "backgroundColor": "#03df94",
                "datalabels": {{
                    "display": false
                }}
            }},
            {{
                "label": "Fail",
                "data": {fail_data},
                "backgroundColor": "#ed6d80",
                "failureRateData": {failure_rates_json},
                "datalabels": {{
                    "display": true,
                    "align": "end",
                    "anchor": "end",
                    "formatter": (function(value, ctx) {{ return ctx.dataset.failureRateData[ctx.dataIndex]; }}),
                    "font": {{
                        "weight": "bold"
                    }},
                    "color": "#727273"
                }}
            }}
        ]
    }},
    "options": {{
        "scales": {{
            "xAxes": [{{
                "stacked": true,
                "offset": true,
            }}],
            "yAxes": [{{
                "stacked": true,
                "ticks": {{
                    "suggestedMin": 0,
                    "suggestedMax": {floor(max([i+j for i, j in zip(success_data, fail_data)])/50)*50+100},
                }},
            }}]
        }},
        "plugins": {{
            "datalabels": {{
                "display": false
            }}
        }}
    }}
}}"""


print("Shareable Chart URL:", qc.get_short_url())


input("\nPress Enter to exit...")