import aiohttp
import asyncio
from aiohttp import ClientSession

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class Currency:
    """
    Class that represents currency
    """

    num_code: int
    char_code: str
    nominal: int
    name: str
    value: float


class CentralBankAPI:
    """
    Class that parses data from Russian Central bank using it's API
    """

    def __init__(self, aiohttp_session: ClientSession = None):
        """
        Constructor of the class

        :param aiohttp_session: Session that will be used to make asynchronous requests.
        If None provided, than new will be created
        """

        self.session = aiohttp_session if aiohttp_session else ClientSession()

        # URL to Central bank website
        self._base_url = 'https://www.cbr.ru/scripts'

    async def __get_all_currencies_rates(self) -> Dict:
        """
        Internal method that requests exchange rates of all currencies from Centralbank
        :return:
        """
        async with self.session.get(f'{self._base_url}/XML_daily.asp') as request:
            return {'http_code': request.status,
                    'content': await request.text()}

    async def get_currency_info(self, currency_char_code) -> Optional[Currency]:
        import xml.etree.ElementTree as ET

        all_currencies_info = await self.__get_all_currencies_rates()

        # Check if API request was successful
        if all_currencies_info['http_code'] != 200:
            # Todo replace or remove base exception raising
            raise Exception

        document_root = ET.fromstring(all_currencies_info['content'])

        # Iterate through root children
        for currency in document_root:
            # Check currency CharCode
            # if it is currency that we are looking for than return Currency object
            if currency.find('CharCode').text.lower() == currency_char_code.lower():
                return Currency(num_code=int(currency.find('NumCode').text),
                                char_code=currency_char_code,
                                nominal=int(currency.find('Nominal').text),
                                name=currency.find('Name').text,

                                # Replacing comma with dot so it could be converted to the float
                                value=float(currency.find('Value').text.replace(',', '.', 1)),
                                )

        return None
