import asyncio
import json
from modules.api.services import get_country_and_operators
import os


class CountrySubscription:
    path = os.path.join(os.getcwd(), 'modules',
                        'subscription', 'countries_data.json')

    template = {
        'users': [],
        'countries': []
    }

    def __init__(self, bot) -> None:
        self.bot = bot
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump(self.template, file, ensure_ascii=False, indent=4)

    async def get_users(self) -> list[int]:
        with open(self.path, 'r', encoding='utf-8') as file:
            return json.load(file)['users']

    async def get_countries(self):
        return [i['name'] for i in (await get_country_and_operators())]

    async def get_countries_from_file(self):
        with open(self.path, encoding='utf-8') as file:
            return json.load(file)['countries']

    async def add_countries(self, countries: list):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        data.update({'countries': countries})
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def add_user(self, user_id: int):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        users = await self.get_users()
        users.append(user_id)
        data.update({'users': users})
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def delete_user(self, user_id: int):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        users = await self.get_users()
        users.remove(user_id)
        data.update({'users': users})
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def check_countries(self):
        countries = await self.get_countries()
        cache = await self.get_countries_from_file()
        if countries != cache:
            # print(
            #     f'new_country(ies): {", ".join(set(countries) - set(cache))}')
            await self.notify_users(", ".join(set(countries) - set(cache)))
            await self.add_countries(countries)

    async def notify_users(self, countries: str):
        for user in (await self.get_users()):
            self.bot.send_message(user, f"Новые страны: {countries}")

    async def run_countries_monitoring(self):
        while True:
            await self.check_countries()
            await asyncio.sleep(15)
