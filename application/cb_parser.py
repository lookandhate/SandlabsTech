import aiohttp
import asyncio
from aiohttp import ClientSession

from typing import Dict, Optional, List
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
        Internal method that requests exchange rates of all currencies from Central bank
        :return:
        """

        async with await self.session.get(f'{self._base_url}/XML_daily.asp') as request:
            return {'http_code': request.status,
                    'content': await request.text()}

    async def get_currency_info(self, currency_char_code: str) -> Optional[Currency]:
        """
        Retrieves and returns information about currency
        :param currency_char_code: Currency code in ISO 4217 format
        :return:
        """

        # Special case.
        # Return Hard-coded info, because API does not provide info about RUB itself

        if currency_char_code.lower() == 'rub':
            return Currency(000, 'RUB', 1, 'Russian ruble', 1)

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

    async def convert_currencies(self, from_currency: str, to_currency: str) -> float:
        """
        Finds proportion between two currrencies using it's ratio to RUB
        :param from_currency: Currency to convert from
        :param to_currency: Currency to convert to
        :return: currency 1 / currency 2
        """

        from_currency_info = await self.get_currency_info(from_currency)
        to_currency_info = await self.get_currency_info(to_currency)

        from_rubble_ratio = from_currency_info.value / from_currency_info.nominal
        to_rubble_ration = to_currency_info.value / to_currency_info.nominal

        proportion = from_rubble_ratio / to_rubble_ration

        return proportion

    async def get_information_about_all_currencies(self):
        import xml.etree.ElementTree as ET

        all_currencies_info = await self.__get_all_currencies_rates()

        currencies: List[Currency] = list()
        # Check if API request was successful
        if all_currencies_info['http_code'] != 200:
            # Todo replace or remove base exception raising
            raise Exception

        document_root = ET.fromstring(all_currencies_info['content'])
        # Iterate through root children
        for currency in document_root:
            currencies.append(Currency(num_code=int(currency.find('NumCode').text),
                                       char_code=currency.find('CharCode').text,
                                       nominal=int(currency.find('Nominal').text),
                                       name=currency.find('Name').text,
                                       # Replacing comma with dot so it could be converted to the float
                                       value=float(currency.find('Value').text.replace(',', '.', 1)),
                                       )
                              )

        return currencies
