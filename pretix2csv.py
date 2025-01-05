"""
This script converts pretix json export to csv format that this badge generator accepts.

At the change input and out file names and id of a company name question. Look at the raw dump data to find it"
"""

import csv
import json
from collections import Counter
from pathlib import Path

INPUT_FILE_PATH = Path("pycon2024_pretixdata.json")
OUTPUT_FILE_PATH = Path("output.csv")
COMPANY_QUESTION_ID = 126160
# INPUT_FILE_PATH = False
# OUTPUT_FILE_PATH = False
# COMPANY_QUESTION_ID = False
# Change value of this id.
# In 2024 company name was under a question field with id 126160.
# This year it should obviously be different, so take a look at the raw pretix export and change the value


if not all((INPUT_FILE_PATH, OUTPUT_FILE_PATH, COMPANY_QUESTION_ID)):
    raise RuntimeError("Not all global variables are set. Go int the script and change them")


if __name__ == "__main__":
    with INPUT_FILE_PATH.open() as f:
        data = json.load(f)
    data = data["event"]
    print(data.keys())
    print(len(data["orders"]))
    id2ticket_variations_name = {}
    for item in data["items"][0]["variations"]:
        id2ticket_variations_name[item["id"]] = item["name"]
    print(id2ticket_variations_name)
    id2cat = {}
    for d in data["items"]:
        id2cat[d["id"]] = d["name"]
    print(id2cat)
    print(data["orders"][0].keys())
    orders = []
    for order in data["orders"]:
        orders += order["positions"]
    print(len(orders))
    for order in orders:
        order["item_name"] = id2cat[order["item"]]
        order["company_name"] = None
        for answer in order["answers"]:
            if answer["question"] == COMPANY_QUESTION_ID:
                order["company_name"] = answer["answer"]
            order["variation_name"] = id2ticket_variations_name.get(order["variation"])
    pretix2helio = {
        "Speaker ticket": "Speakers",
        "Business": "Business",
        "Organization ticket": "Volunteers and board",
        "Sponsor ticket": "Sponsors",
        "Student ticket": "Student",
    }

    orders_filtered = []
    for order in orders:
        if order["item_name"] != "T-shirt (free)":
            first_name, last_name = order["attendee_name"].split(maxsplit=1)
            dct_to_add = {
                "Given name": first_name,
                "Family name": last_name,
                "Company": order["company_name"],
                "ticket_type": pretix2helio.get(order["item_name"], order["item_name"]),
                "variation": order["variation_name"],
                "job_title": "",
                "Status": "paid",
            }
            orders_filtered.append(dct_to_add)
    orders_sorted = sorted(orders_filtered, key = lambda x: x["Given name"])
    cntr_first_names = Counter(entry["Given name"][0] for entry in orders_sorted)
    cntr_last_names = Counter(entry["Family name"][0] for entry in orders_sorted)
    print(cntr_first_names)
    print(cntr_last_names)
    with OUTPUT_FILE_PATH.open("w") as f:
        writer = csv.DictWriter(f, orders_filtered[0].keys())
        writer.writeheader()
        writer.writerows(orders_filtered)
