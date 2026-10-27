"""Load the dataset.json file and create a python object (array) from it"""
import json

import helpers.common_import as ci

with open("dataset.json", "r") as file:
    dataset = json.load(file)

results = ci.run_eval(dataset)
print(json.dumps(results, indent=2))