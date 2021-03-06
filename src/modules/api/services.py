import json
from typing import Dict, List
from aiohttp import ClientSession
from modules.config.env_config import API_KEY, LANG
from dataclasses import dataclass


@dataclass
class _ContriesAndOperatorsResponse:
    id: int
    name: str
    operators: List[Dict[str, str]]


@dataclass
class _ServicesAndCostsResponse:
    id: int
    name: str
    price: float
    quantity: int


exceptions = ('NO_BALANCE', 'ACCESS_CANCEL',
              'ACCESS_RETRY_GET', 'NO_NUMBERS')
API_URL = "https://sms-service-online.com/stubs/handler_api?api_key={API_KEY}&lang={LANG}&action={ACTION}"


async def get_balance(api_key: str = API_KEY, lang: str = LANG) -> float:
    """
    action: `getBalance`
    """
    async with ClientSession() as session:
        async with session.get(API_URL.format(API_KEY=api_key, LANG=lang, ACTION="getBalance")) as res:
            response = await res.text()
    return float(response)


async def get_country_and_operators(api_key: str = API_KEY, lang: str = LANG) -> List[_ContriesAndOperatorsResponse]:
    """
    action: `getCountryAndOperators`
    """
    async with ClientSession() as session:
        async with session.get(API_URL.format(API_KEY=api_key, LANG=lang, ACTION="getCountryAndOperators")) as res:
            json_response = json.loads(await res.text())
    return json_response


async def get_services_and_cost(operator: str, country: int, api_key: str = API_KEY, lang: str = LANG) -> List[_ServicesAndCostsResponse]:
    """
    action: `getServicesAndCost`
    """
    async with ClientSession() as session:
        async with session.get(f"{API_URL.format(API_KEY=api_key, LANG=lang, ACTION='getServicesAndCost')}&operator={operator}&country={country}") as res:
            json_response = json.loads(await res.text())
    return json_response


async def get_number(service: str, operator: str, country: int, api_key: str = API_KEY, lang: str = LANG) -> str:
    """
    action: `getNumber`
    """
    async with ClientSession() as session:
        async with session.get(f"{API_URL.format(API_KEY=api_key, LANG=lang, ACTION='getNumber')}&service={service}&operator={operator}&country={country}") as res:
            text = await res.text()
    return text


async def set_status(id_: int, status: int, api_key: str = API_KEY, lang: str = LANG) -> str:
    """
    action: `setStatus`
    """
    async with ClientSession() as session:
        async with session.post(f"{API_URL.format(API_KEY=api_key, LANG=lang, ACTION='setStatus')}&id={id_}&status={status}") as res:
            response = await res.text()
    return response


async def get_status(id_, api_key: str = API_KEY, lang: str = LANG) -> str:
    """
    action: `getStatus`
    """
    async with ClientSession() as session:
        # print(f"{API_URL.format(API_KEY=api_key, LANG=lang, ACTION='getStatus')}&id={id_}")
        async with session.get(f"{API_URL.format(API_KEY=api_key, LANG=lang, ACTION='getStatus')}&id={id_}") as res:
            response = await res.text()
    return response
