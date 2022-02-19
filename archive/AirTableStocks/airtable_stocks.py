#!/usr/bin/env python3

import json
import os.path
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Dict
import random

import arrow
import attr
import requests


@attr.s
class StockInfo(object):
    ticker = attr.ib(type=str)
    price = attr.ib(converter=float)
    week_ago = attr.ib(converter=float)
    mo_ago = attr.ib(converter=float)
    quarter_ago = attr.ib(converter=float)
    yr_ago = attr.ib(converter=float)
    last_updated = attr.ib(type=str)


@attr.s
class PortfolioItem(object):
    ticker = attr.ib(type=str)
    # Same stock can be present in multiple rows.
    row_ids = attr.ib(type=list)
    count = attr.ib(type=int)
    stock_info = attr.ib(type=StockInfo)


T = TypeVar('T')  # Generic Type
config = json.load(open(os.path.expanduser('~/.airtable_keys.json')))
STOCK_INFO_CSV = os.path.expanduser('~/.airtable_stocks.json')
ALPHA_ADVANTAGE_KEY = config['AlphaAdvantage']
AIRTABLE_KEY = config['Airtable']['Key']
AIRTABLE_BASE_ID = config['Airtable']['BaseId']
STOCKS_TABLE_NAME = 'Stocks'
PORTFOLIO_TABLE_NAME = 'Portfolio'
MAX_RPM = 5


def DateNDaysAgo(n: int) -> str:
    return arrow.utcnow().shift(days=-n).format('YYYY-MM-DD')


def DictToShuffledList(dct: Dict[str, T]) -> List[Tuple[str, T]]:
    ret = list(dct.items())
    random.shuffle(ret)
    return ret


last_aa_request_time = arrow.get(1970, 1, 1)
# Alpha advantage has a MAX_RPS. This must be called before making API call.
def GetAlphaAdvantageApproval():
    global last_aa_request_time
    global MAX_RPM
    next_allowed_time = last_aa_request_time.shift(seconds=int(1 + (60.0 / MAX_RPM)))
    if next_allowed_time < arrow.utcnow():
        print('{} No Wait'.format(arrow.utcnow()))
        last_aa_request_time = arrow.utcnow()
        return
    wait_time = next_allowed_time - arrow.utcnow()
    import time
    print('{} Start Wait. Waiting for '.format(arrow.utcnow()), wait_time)
    time.sleep(wait_time.total_seconds())
    print('{} End Wait'.format(arrow.utcnow()))
    last_aa_request_time = arrow.utcnow()


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
    ignore_keys = {'open', 'high', 'low', 'close', 'volume', 'dividend_amount', 'split_coefficient',
                   'meta_data'}
    if type(response) == list:
        return [CleanupAlphaAdvantageResponse(item) for item in response]
    elif isinstance(response, dict):
        transformed = {transform_key(key): CleanupAlphaAdvantageResponse(value) for key, value in
                       response.items()}
        transformed = {k: float(v) if k in numeric_keys else v for k, v in transformed.items() if
                       k not in ignore_keys}
        if len(transformed) == 1:
            return list(transformed.values())[0]
        else:
            return transformed
    else:
        return response


def GetStockInfo(ticker, existing_stock_info):
    ticker = ticker.upper()
    GetAlphaAdvantageApproval()
    response = requests.get(url='https://www.alphavantage.co/query',
                            params={'function': 'TIME_SERIES_DAILY_ADJUSTED', 'symbol': ticker,
                                    'apikey': ALPHA_ADVANTAGE_KEY,
                                    'outputsize': 'full'}).json()
    close_prices = CleanupAlphaAdvantageResponse(response)
    if not close_prices or not isinstance(close_prices, dict):
        print('{} Fail {}'.format(arrow.utcnow(), ticker))
        # This request failed. If we have old data, return it.
        return existing_stock_info.get(ticker, None)
    print('{} Success {}'.format(arrow.utcnow(), ticker))
    reverse_sorted_dates = sorted(close_prices.keys(), reverse=True)

    # 1w before a sunday is a sunday. There will be no stock info.
    # So we need to find the nearest day before that day.
    def nearest_close_price(days_ago):
        date = DateNDaysAgo(days_ago)
        for market_date in reverse_sorted_dates:
            if market_date <= date:
                return close_prices[market_date]
        return float('nan')

    last_updated = max(close_prices.keys())
    latest_price = close_prices.get(last_updated, float('nan'))
    return StockInfo(ticker=ticker, price=latest_price, last_updated=last_updated,
                     week_ago=nearest_close_price(7),
                     mo_ago=nearest_close_price(31),
                     quarter_ago=nearest_close_price(91),
                     yr_ago=nearest_close_price(365))


def ReadPortfolioTable():
    response = requests.get(
        url='https://api.airtable.com/v0/{}/{}'.format(AIRTABLE_BASE_ID, PORTFOLIO_TABLE_NAME),
        params={'api_key': 'key5s6LLGY7y5wbDp'}).json()
    if 'records' not in response:
        return None
    ret = dict()
    for record in response['records']:
        # Same stock can be present in multiple rows.
        ticker, count, row_id = record['fields']['Ticker'], record['fields']['Quantity'], record[
            'id']
        if ticker in ret:
            existing = ret[ticker]
            existing.count += count
            existing.row_ids.append(row_id)
        else:
            ret[ticker] = PortfolioItem(ticker=ticker, row_ids=[row_id], count=count,
                                        stock_info=None)
    return ret


def ClearStocksTable():
    # Removes all info from stocks table.
    response = requests.get(
        url='https://api.airtable.com/v0/{}/{}'.format(AIRTABLE_BASE_ID, STOCKS_TABLE_NAME),
        params={'api_key': 'key5s6LLGY7y5wbDp'}).json()
    if 'records' not in response:
        return None
    for record in response['records']:
        requests.delete(
            url='https://api.airtable.com/v0/{}/{}/{}'.format(AIRTABLE_BASE_ID, STOCKS_TABLE_NAME,
                                                              record['id']),
            headers={'Authorization': 'Bearer {}'.format(AIRTABLE_KEY)})


def UpdatePortfolioTable(portfolio):
    for pf_item in portfolio.values():
        if not pf_item.stock_info:
            continue
        # Update portfolio table with the latest stock price.
        for row_id in pf_item.row_ids:
            url = 'https://api.airtable.com/v0/{}/{}/{}'.format(AIRTABLE_BASE_ID,
                                                                PORTFOLIO_TABLE_NAME, row_id)
            requests.patch(url=url, headers={'Authorization': 'Bearer {}'.format(AIRTABLE_KEY)},
                           json={'fields': {'Current Price': pf_item.stock_info.price}})


def UpdateStocksTable(portfolio):
    # Delete stocks table data.
    ClearStocksTable()
    # Update the stocks table with new data from portfolio.
    for pf_item in portfolio.values():
        if not pf_item.stock_info:
            continue
        url = 'https://api.airtable.com/v0/{}/{}'.format(AIRTABLE_BASE_ID, STOCKS_TABLE_NAME)

        def historical_price(old_price, current_price):
            old_price, current_price = float(old_price), float(current_price)
            up_down = '⬆️' if (current_price > old_price) else '🔻'
            return '${} {:.1f}% {}'.format(old_price,
                                           abs(current_price - old_price) * 100.0 / old_price,
                                           up_down)

        stock_info = pf_item.stock_info
        record = {
            'fields': {
                'Name': stock_info.ticker,
                'Price': stock_info.price,
                '1w ago': historical_price(stock_info.week_ago, stock_info.price),
                '1mo ago': historical_price(stock_info.mo_ago, stock_info.price),
                '3mo ago': historical_price(stock_info.quarter_ago, stock_info.price),
                '1yr ago': historical_price(stock_info.yr_ago, stock_info.price),
                'Last updated': stock_info.last_updated,
                'Value Owned': stock_info.price * pf_item.count
            }}
        print(url)
        print(record)
        requests.post(url=url, headers={'Authorization': 'Bearer {}'.format(AIRTABLE_KEY)},
                      json=record)


def WriteStocksToCSV(fn, ticker_to_stocks):
    import csv
    with open(fn, 'w') as csvfile:
        csv_writer = csv.DictWriter(csvfile,
                                    fieldnames=[field.name for field in attr.fields(StockInfo)],
                                    delimiter=',')
        csv_writer.writeheader()
        for _, stock in ticker_to_stocks.items():
            csv_writer.writerow(attr.asdict(stock))


def ReadStocksFromCSVOrReturnEmpty(fn):
    try:
        import csv
        with open(fn, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            return {s['ticker']: StockInfo(**s) for s in csv_reader}
    except Exception:
        return dict()


def UpdateAirtable():
    def EnhancePortfolioItem(portfolio_item, stock_info):
        # Adds stock info to the portfolio item.
        portfolio_item.stock_info = stock_info
        return portfolio_item

    # Read: Existing stock info from disk.
    existing_stock_info = ReadStocksFromCSVOrReturnEmpty(STOCK_INFO_CSV)
    # Read: Stocks, Count, Airtable row ids
    portfolio_without_price = ReadPortfolioTable()
    if portfolio_without_price is None:
        # Failure.
        return

    # Compute: StockInfo for all the stocks and enhance the portfolio info.
    portfolio_with_price = {
        ticker: EnhancePortfolioItem(folio_item, GetStockInfo(ticker, existing_stock_info)) for
        ticker, folio_item in
        # Shuffle the list to make sure the same stocks dont get rate limited again and again.
        DictToShuffledList(portfolio_without_price)
        }
    # Update tables
    UpdatePortfolioTable(portfolio_with_price)
    UpdateStocksTable(portfolio_with_price)
    # Update Stock Info CSV
    WriteStocksToCSV(STOCK_INFO_CSV,
                     {ticker: portfolio_item.stock_info for ticker, portfolio_item in
                      portfolio_with_price.items() if
                      portfolio_item.stock_info is not None})


if __name__ == '__main__':
    UpdateAirtable()
