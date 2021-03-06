import json
import os


async def update_param(param: str):
    with open(os.path.abspath('modules/statistics/stats.json'), 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
        json_data[param] += 1
    with open(os.path.abspath('modules/statistics/stats.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_data, ensure_ascii=False))


async def get_params():
    with open(os.path.abspath('modules/statistics/stats.json'), 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
        answer = 'Общая статистика\n\n'
        for param, num in json_data.items():
            answer += f'{param}: {num}\n'
        return answer
