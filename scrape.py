#!/usr/bin/env python2.7

import os
import sys
import requests

from bs4 import BeautifulSoup

# import logging

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


HOST = 'https://www.sharecoffeeroasters.com'
SIGN_IN_URL = HOST + '/wholesalers/sign_in'
NEW_ORDER_URL = HOST + '/wholesale_orders/new'

COOKIE = '_ShareCoffee_session'


def login(username, password):
    '''
    Login to the Share wholesalers site - returns a cookie jar.
    '''
    r = requests.get(SIGN_IN_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    csrf_param = soup.find('meta', attrs={'name': 'csrf-param'}).attrs['content']
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'}).attrs['content']

    form = {
        'commit': 'Log in',
        'wholesaler[email]': username,
        'wholesaler[password]': password,
        'wholesaler[remember_me]': 0,
        csrf_param: csrf_token,
    }

    r = requests.post(SIGN_IN_URL, data=form, cookies=r.cookies)
    r.raise_for_status()
    return r.cookies


def main():
    cookies = login(os.environ['SHARE_EMAIL'], os.environ['SHARE_PASSWORD'])

    r = requests.get(NEW_ORDER_URL, cookies=cookies)
    r.raise_for_status()
    # print('%r' % r)

    # for li in soup.find_all('li', class_='site-listing'):
    #     n = int(li.find('div', class_='count').string)
    #     domain = li.find('p', class_='desc-paragraph').a['href'].replace('/siteinfo/', '')
    #     print('%d\t%s' % (n, domain))

if __name__ == '__main__':
    sys.exit(main())
