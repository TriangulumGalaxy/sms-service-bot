import json


async def update_param(param: str):
    with open('modules/statistics/stats.json', 'r') as f:
        json_data = json.load(f)
        json_data[param] += 1
    with open('modules/statistics/stats.json', 'w') as f:
        f.write(json.dumps(json_data))


async def get_param(param: str) -> int:
    with open('modules/statistics/stats.json', 'r') as f:
        json_data = json.load(f)
        return json_data[param]
