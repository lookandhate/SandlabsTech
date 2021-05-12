import aiohttp
import asyncio
from aiohttp import ClientSession

from pprint import pprint


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

    async def __get_all_currencies_rates(self):
        """
        Internal method that requests exchange rates of all currencies from Centralbank
        :return:
        """
        async with self.session.get(f'{self._base_url}/XML_daily.asp') as request:
            return {'http_code': request.status,
                    'content': await request.text()}

    async def get_currency_info(self, currency):
        import xml

        all_currencies_info = self.__get_all_currencies_rates()

        if all_currencies_info['http_code'] != 200:
            # Todo replace or remove base exception raising
            raise Exception

async def test():
    CB = CentralBankAPI()
    data = await CB.get_currency_rates()
    pprint(data)


asyncio.new_event_loop().run_until_complete(test())
