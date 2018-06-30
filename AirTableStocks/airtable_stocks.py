#!/usr/bin/env python3

import os.path
import json
import attr
import requests
import math


@attr.s
class StockInfo(object):
    ticker = attr.ib(type=str)
    price = attr.ib(type=float)
    week_ago = attr.ib(type=float)
    mo_ago = attr.ib(type=float)
    quarter_ago = attr.ib(type=float)
    yr_ago = attr.ib(type=float)
    last_updated = attr.ib(type=str)


keys = json.load(open(os.path.expanduser('~/.airtable_keys.json')))
ALPHA_ADVANTAGE_KEY = keys['AlphaAdvantage']
AIRTABLE_KEY = keys['Airtable']['Key']
AIRTABLE_BASE_ID = keys['Airtable']['BaseId']
STOCKS_TABLE_NAME = 'Stocks'
PORTFOLIO_TABLE_NAME = 'Portfolio'


def CleanupAlphaAdvantageResponse(response):
    def transform_key(key):
        import re
        key = key.lower()
        key = re.sub(r'^\d+\.\s+', '', key)
        key = re.sub(r'[()]', ' ', key)
        key = key.strip()
        key = re.sub(r'\s+', '_', key)
        return key

    numeric_keys = {'adjusted_close'}
    ignore_keys = {'open', 'high', 'low', 'close', 'volume', 'dividend_amount', 'split_coefficient', 'meta_data'}
    if type(response) == list:
        return [CleanupAlphaAdvantageResponse(item) for item in response]
    elif isinstance(response, dict):
        transformed = {transform_key(key): CleanupAlphaAdvantageResponse(value) for key, value in response.items()}
        transformed = {k: float(v) if k in numeric_keys else v for k, v in transformed.items() if k not in ignore_keys}
        if len(transformed) == 1:
            return list(transformed.values())[0]
        else:
            return transformed
    else:
        return response


def DateNDaysAgo(n):
    import arrow
    return arrow.utcnow().shift(days=n).format('YYYY-MM-DD')


def GetStockInfo(ticker):
    ticker = ticker.upper()
    response = requests.get(url='https://www.alphavantage.co/query',
                            params={'function': 'TIME_SERIES_DAILY_ADJUSTED', 'symbol': ticker,
                                    'apikey': ALPHA_ADVANTAGE_KEY,
                                    'outputsize': 'full'}).json()
    close_prices = CleanupAlphaAdvantageResponse(response)
    if not close_prices:
        return None
    reverse_sorted_dates = sorted(close_prices.keys(), reverse=True)

    def nearest_close_price(days_ago):
        date = DateNDaysAgo(days_ago)
        for market_date in reverse_sorted_dates:
            if market_date <= date:
                return close_prices[market_date]
        return math.nan

    last_updated = max(close_prices.keys())
    latest_price = close_prices.get(last_updated, math.nan)
    return StockInfo(ticker=ticker, price=latest_price, last_updated=last_updated,
                     week_ago=nearest_close_price(7),
                     mo_ago=nearest_close_price(31),
                     quarter_ago=nearest_close_price(91),
                     yr_ago=nearest_close_price(365))


@attr.s
class PortfolioItem(object):
    ticker = attr.ib(type=str)
    row_ids = attr.ib(type=list)
    count = attr.ib(type=int)
    stock_info = attr.ib(type=StockInfo)


def ReadPortfolioTable():
    response = requests.get(url='https://api.airtable.com/v0/{}/{}'.format(AIRTABLE_BASE_ID, PORTFOLIO_TABLE_NAME),
                            params={'api_key': 'key5s6LLGY7y5wbDp'}).json()
    if 'records' not in response:
        return None
    ret = dict()
    for record in response['records']:
        ticker, count, row_id = record['fields']['Ticker'], record['fields']['Quantity'], record['id']
        if ticker in ret:
            existing = ret[ticker]
            existing.count += count
            existing.row_ids.append(row_id)
        else:
            ret[ticker] = PortfolioItem(ticker=ticker, row_ids=[row_id], count=count, stock_info=None)
    return ret


def UpdatePortfolioTable(portfolio):
    pass


def UpdateStocksTable(portfolio):
    pass


def UpdateAirtable():
    # Update: Portfolio
    # Update: Stocks
    def EnhancePortfolioItem(portfolio_item, stock_info):
        portfolio_item.stock_info = stock_info
        return portfolio_item

    # Read: Stocks, Count, Airtable row ids
    portfolio_without_price = ReadPortfolioTable()
    print(portfolio_without_price)
    if portfolio_without_price is None:
        return
    # Compute: StockInfo
    # Update: portfolio dict
    portfolio_with_price = {ticker: EnhancePortfolioItem(folio_item, GetStockInfo(ticker)) for ticker, folio_item in
                            portfolio_without_price.items()}
    print(portfolio_with_price)
    # Update tables
    UpdatePortfolioTable(portfolio_with_price)
    UpdateStocksTable(portfolio_with_price)


UpdateAirtable()
