# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import json
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import OrderNotFound


class tidebit (Exchange):

    def describe(self):
        return self.deep_extend(super(tidebit, self).describe(), {
            'id': 'tidebit',
            'name': 'TideBit',
            'countries': ['HK'],
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'fetchDepositAddress': True,
                'CORS': True,
                'fetchTickers': True,
                'fetchOHLCV': True,
                'withdraw': True,
            },
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '4h': '240',
                '12h': '720',
                '1d': '1440',
                '3d': '4320',
                '1w': '10080',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/39034921-e3acf016-4480-11e8-9945-a6086a1082fe.jpg',
                'api': 'https://www.tidebit.com',
                'www': 'https://www.tidebit.com',
                'doc': 'https://www.tidebit.com/documents/api_v2',
            },
            'api': {
                'public': {
                    'get': [
                        'v2/markets',  # V2MarketsJson
                        'v2/tickers',  # V2TickersJson
                        'v2/tickers/{market}',  # V2TickersMarketJson
                        'v2/trades',  # V2TradesJson
                        'v2/trades/{market}',  # V2TradesMarketJson
                        'v2/order_book',  # V2OrderBookJson
                        'v2/order',  # V2OrderJson
                        'v2/k_with_pending_trades',  # V2KWithPendingTradesJson
                        'v2/k',  # V2KJson
                        'v2/depth',  # V2DepthJson
                    ],
                    'post': [],
                },
                'private': {
                    'get': [
                        'v2/deposits',  # V2DepositsJson
                        'v2/deposit_address',  # V2DepositAddressJson
                        'v2/deposit',  # V2DepositJson
                        'v2/members/me',  # V2MembersMeJson
                        'v2/addresses/{address}',  # V2AddressesAddressJson
                    ],
                    'post': [
                        'v2/order/delete',  # V2OrderDeleteJson
                        'v2/order',  # V2OrderJson
                        'v2/order/multi',  # V2OrderMultiJson
                        'v2/order/clear',  # V2OrderClearJson
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
                'funding': {
                    'tierBased': False,
                    'percentage': True,
                    'withdraw': {},  # There is only 1% fee on withdrawals to your bank account.
                },
            },
            'exceptions': {
                '2002': InsufficientFunds,
                '2003': OrderNotFound,
            },
        })

    async def fetch_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        response = await self.privateGetV2DepositAddress(self.extend({
            'currency': currency['id'],
        }, params))
        if 'success' in response:
            if response['success']:
                address = self.safe_string(response, 'address')
                tag = self.safe_string(response, 'addressTag')
                return {
                    'currency': code,
                    'address': self.check_address(address),
                    'tag': tag,
                    'info': response,
                }

    async def fetch_markets(self):
        markets = await self.publicGetV2Markets()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['id']
            symbol = market['name']
            baseId, quoteId = symbol.split('/')
            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'info': market,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privateGetV2MembersMe()
        balances = response['accounts']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currencyId = balance['currency']
            code = currencyId.upper()
            if currencyId in self.currencies_by_id:
                code = self.currencies_by_id[currencyId]['code']
            account = {
                'free': float(balance['balance']),
                'used': float(balance['locked']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        if limit is None:
            request['limit'] = limit  # default = 300
        request['market'] = market['id']
        orderbook = await self.publicGetV2Depth(self.extend(request, params))
        timestamp = orderbook['timestamp'] * 1000
        return self.parse_order_book(orderbook, timestamp)

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['at'] * 1000
        ticker = ticker['ticker']
        symbol = None
        if market is not None:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            'ask': self.safe_float(ticker, 'sell'),
            'bidVolume': None,
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'change': None,
            'percentage': None,
            'previousClose': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'vol'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        tickers = await self.publicGetV2Tickers(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = None
            symbol = id
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            else:
                base = id[0:3]
                quote = id[3:6]
                base = base.upper()
                quote = quote.upper()
                base = self.common_currency_code(base)
                quote = self.common_currency_code(quote)
                symbol = base + '/' + quote
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetV2TickersMarket(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_ticker(response, market)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['created_at'])
        return {
            'id': str(trade['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': self.safe_float(trade, 'price'),
            'amount': self.safe_float(trade, 'volume'),
            'cost': self.safe_float(trade, 'funds'),
            'info': trade,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetV2Trades(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            ohlcv[1],
            ohlcv[2],
            ohlcv[3],
            ohlcv[4],
            ohlcv[5],
        ]

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        if limit is None:
            limit = 30  # default is 30
        request = {
            'market': market['id'],
            'period': self.timeframes[timeframe],
            'limit': limit,
        }
        if since is not None:
            request['timestamp'] = since
        else:
            request['timestamp'] = 1800000
        response = await self.publicGetV2K(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def parse_order(self, order, market=None):
        symbol = None
        if market is not None:
            symbol = market['symbol']
        else:
            marketId = order['market']
            symbol = self.markets_by_id[marketId]['symbol']
        timestamp = self.parse8601(order['created_at'])
        state = order['state']
        status = None
        if state == 'done':
            status = 'closed'
        elif state == 'wait':
            status = 'open'
        elif state == 'cancel':
            status = 'canceled'
        return {
            'id': str(order['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': order['ord_type'],
            'side': order['side'],
            'price': self.safe_float(order, 'price'),
            'amount': self.safe_float(order, 'volume'),
            'filled': self.safe_float(order, 'executed_volume'),
            'remaining': self.safe_float(order, 'remaining_volume'),
            'trades': None,
            'fee': None,
            'info': order,
        }

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        order = {
            'market': self.market_id(symbol),
            'side': side,
            'volume': str(amount),
            'ord_type': type,
        }
        if type == 'limit':
            order['price'] = str(price)
        response = await self.privatePostV2Order(self.extend(order, params))
        market = self.markets_by_id[response['market']]
        return self.parse_order(response, market)

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        result = await self.privatePostV2OrderDelete({'id': id})
        order = self.parse_order(result)
        status = order['status']
        if status == 'closed' or status == 'canceled':
            raise OrderNotFound(self.id + ' ' + self.json(order))
        return order

    async def withdraw(self, currency, amount, address, tag=None, params={}):
        self.check_address(address)
        await self.load_markets()
        result = await self.privatePostWithdraw(self.extend({
            'currency': currency.lower(),
            'sum': amount,
            'address': address,
        }, params))
        return {
            'info': result,
            'id': None,
        }

    def nonce(self):
        return self.milliseconds()

    def encode_params(self, params):
        return self.urlencode(self.keysort(params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/' + 'api/' + self.implode_params(path, params) + '.json'
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'] + request
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            sortedByKey = self.keysort(self.extend({
                'access_key': self.apiKey,
                'tonce': nonce,
            }, params))
            query = self.urlencode(sortedByKey)
            payload = method + '|' + request + '|' + query
            signature = self.hmac(self.encode(payload), self.encode(self.secret))
            suffix = query + '&signature=' + signature
            if method == 'GET':
                url += '?' + suffix
            else:
                body = suffix
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, code, reason, url, method, headers, body):
        if code == 400:
            response = json.loads(body)
            error = self.safe_value(response, 'error')
            errorCode = self.safe_string(error, 'code')
            feedback = self.id + ' ' + self.json(response)
            exceptions = self.exceptions
            if errorCode in exceptions:
                raise exceptions[errorCode](feedback)
            # fallback to default error handler
