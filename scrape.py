#!/usr/bin/env python2.7

import os
import sys
import requests

from bs4 import BeautifulSoup


HOST = 'https://www.sharecoffeeroasters.com'
SIGN_IN_URL = HOST + '/wholesalers/sign_in'
NEW_ORDER_URL = HOST + '/wholesale_orders/new'

SIZES = ['6oz', '12oz', '3lb']


def share_session(username, password):
    '''
    Returns an authenticated session for the Share wholesalers site.
    '''
    session = requests.Session()

    r = session.get(SIGN_IN_URL)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    # cross-site request forgery protection
    param = soup.find('meta', attrs={'name': 'csrf-param'}).attrs['content']
    token = soup.find('meta', attrs={'name': 'csrf-token'}).attrs['content']

    form = {
        'commit': 'Log in',
        'wholesaler[email]': username,
        'wholesaler[password]': password,
        'wholesaler[remember_me]': 0,
        param: token,
    }

    r = session.post(SIGN_IN_URL, data=form, cookies=r.cookies)
    r.raise_for_status()

    return session


def parse_offering(li):
    row = li.div
    # find our non-whitespace children
    children = [c for c in row.contents if c.name]

    name_col = children[0]
    price_col = children[1]

    name = ' '.join(name_col.div.get_text().split())
    pricepoints = {}

    # for 6oz bag
    msrp = ''

    rows = [c for c in price_col.children if c.name == 'div' and 'row' in c.attrs.get('class', [])]
    for r in rows:
        size = r.find_all('div', class_='col-xs-3')[0].get_text().strip()
        # text is '6oz:', remove the trailing ':'
        if size[-1] == ':':
            size = size[0:-1]

        price_container = r.find_all('div', class_='input-group-addon')[0]
        price_div = price_container.find_all('div', class_='text-left')[0]
        price = price_div.contents[0].strip()
        if size == '6oz':
            msrp = price_div.find_all('small', class_='small')[0].get_text()
            msrp = msrp.strip()
            #msrp = msrp.strip().split()[1][:-1]
        pricepoints[size] = price

    return {
        'name': name,
        'msrp': msrp,
        'pricepoints': pricepoints,
    }


def main():
    email = os.environ['SHARE_EMAIL']
    password = os.environ['SHARE_PASSWORD']

    session = share_session(email, password)

    r = session.get(NEW_ORDER_URL)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    # find the table of current coffee orderings in the HTML form
    offerings = soup.find('form').find_all('ul', class_='list-group')[0]
    # filter out whitespace elements
    offerings = [c for c in offerings.children if c.name]
    for li in offerings:
        coffee = parse_offering(li)

        # check that the sizes we got from the API match the hardcoded
        # values in this script (we hardcode them to ensure printing
        # out rows in the ideal order)
        seen_sizes = set(coffee['pricepoints'].keys())
        bad_sizes = seen_sizes.symmetric_difference(SIZES)
        if len(bad_sizes):
            sys.stderr.write('ERROR: unknown pricepoints: %s' % (bad_sizes,))
            return 1

        for size in SIZES:
            price = coffee['pricepoints'][size]

            data = '%s\t%s\t%s' % (coffee['name'], size, price)
            if size == '6oz':
                data += '\t%s' % coffee['msrp']

            sys.stdout.write(data + '\n')


if __name__ == '__main__':
    sys.exit(main())
