import aiohttp

from sanic import Sanic
from sanic.response import json

from app.cb_parser import CentralBankAPI

app = Sanic('app')
currency_api_client: CentralBankAPI = None


@app.listener('before_server_start')
async def init(app, loop):
    global currency_api_client
    app.aiohttp_session = aiohttp.ClientSession(loop=loop)
    currency_api_client = CentralBankAPI(app.aiohttp_session)


@app.listener('after_server_stop')
async def finish(app, loop):
    loop.run_until_complete(app.aiohttp_session.close())
    loop.close()


@app.route('/')
async def homepage(request):
    return json({"hello": "world"})


@app.route('/api/course/<currency>', methods=['GET'])
async def currency_course(request, currency):
    data = await currency_api_client.get_currency_info(currency)
    if data is not None:
        return json({
            'currency': data.char_code,
            'rub_course': round(data.value / data.nominal, 3)
        })

    return json({'message': 'No currency with that name was found. Check spelling and try again'})




app.run(host="0.0.0.0", port=8000)