import urllib
import sys
import json
from collections import defaultdict as dd
import argparse
from tabulate import tabulate

# Usage https://asciinema.org/a/18026

url_format = 'http://query.yahooapis.com/v1/public/yql?{0}&format=json'
query_format = '''select LastTradePriceOnly,symbol,Name
           from yahoo.finance.quotes
           where symbol in ({0})'''

def give_price(quotes):
    quotes = ','.join(('"' + q.strip() + '"' for q in quotes))
    query = query_format.format(quotes)
    query = urllib.urlencode(
        {'q': query, 'env': 'http://datatables.org/alltables.env'})
    url = url_format.format(query)

    res = urllib.urlopen(url).read()
    res = json.loads(res)['query']['results']['quote']
    return res


def tabulate_and_print(header, data):
    data = [ d[:-1].split(",") for d in data]
    header = header[:-1].split(",")
    print tabulate(data, headers = header,floatfmt=".2f")

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inp', '-i', type=str, default='history', help='input file containing stock purchase history')
    parser.add_argument('--out','-o', type=str, default='result.csv', help='output csv')
    parser.add_argument('--verbose', '-v', action='store_true',help='verbose flag' )
    args = parser.parse_args()

    if args.verbose:
        print "verbose mode"
        print "input file : {}".format(args.inp)
        print "output file : {}".format(args.out)

    history = dd(lambda : (0,0))
    config_file = args.inp

    for line in open(config_file):
        cr = line.split(' ')
        mult = -1
        if cr[0] == '+': mult = 1
        prev = history[cr[1]]
        pres = (prev[0] + mult*int(cr[2]), prev[1] + mult*float(cr[3]))
        history[cr[1]] = pres

    pres_value = give_price(history.keys())

    out = open(args.out, 'w')
    header = "symbol,price,avg_spent,spent,pres_val,profit\n"
    out.write(header)
    data = []
    for stocks in pres_value:
        stock = stocks['symbol']
        count, spent = history[stock]
        price = float(stocks['LastTradePriceOnly'])
        pres_value = price * count
        profit = pres_value - spent
        line = "{0},{1},{2},{3},{4},{5}\n".format(
                            stock, price, spent/count, 
                            spent, pres_value, profit)
        data.append(line)
        out.write(line)
    if args.verbose:
        tabulate_and_print(header, data)
    out.close()

if __name__ == '__main__':
    main()
