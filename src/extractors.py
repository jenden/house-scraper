import re
import requests
from numpy.random import exponential
import time
import logging
from bs4 import BeautifulSoup

BASE_URL = 'https://www.rew.ca'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) '
                         'Version/7.0.3 Safari/7046A194A'}

def get_page_soup(url):
    # sometimes links are relative, add base when needed
    if not url.startswith('https://'):
        url = BASE_URL + url
    page = requests.get(url, headers=HEADERS)
    return BeautifulSoup(page.text, 'html5lib')


class Ladle:
    """
    Ladle class manages requests and ensures they are metered so they don't overwhelm the REW servers. In the
     future it may also have the ability to change IP address of the VM in case REW starts blocking requests.
    """
    __last_request = time.time()
    __random_time = lambda: exponential(2, 1)[0]

    @staticmethod
    def get_soup(url):
        timeout = Ladle.__random_time()
        if Ladle.__last_request + timeout > time.time():
            time.sleep(timeout)

        logging.info('Requested url: {} after {:.1f}s delay'.format(url, timeout))
        return get_page_soup(url)


def main_content(soup):
    """Returns the section in the page which contains the listing"""
    return soup.find('section', class_='container maincontentspacer')


def listing_id(soup):
    """Returns the listing id from the html head"""
    import re
    url = soup.head.link['href']
    return listing_id_from_url(url)


def listing_id_from_url(url):
    return re.findall('(?<=properties/).*(?=/)', url)[0]


def listing_id_mc(mc):
    """Returns the listing id from the property description"""
    pass


def street_address(mc):
    return mc.find('span', itemprop='streetAddress').text.strip()


def city(mc):
    return mc.find('span', itemprop='addressLocality').text.strip()


def province(mc):
    return mc.find('span', itemprop='addressRegion').text.strip()


def postal_code(mc):
    return mc.find('span', itemprop='postalCode').text.strip()

def list_price(mc):
    list_price = mc.find('div', class_='propertyheader-price').text.strip()
    return price_str_to_int(list_price())


def price_str_to_int(price):
    return int(price.strip('$').replace(',', ''))


def square_footage(mc):
    summary_bar = mc.find('div', class_='summarybar')
    sqft_span = summary_bar.find(string=re.compile('Sqft')).findParent().text
    return int(re.findall(r'\d+', sqft_span)[0])


def beds(mc):
    summary_bar = mc.find('div', class_='summarybar')
    beds_span = summary_bar.find(string=re.compile('Bed')).findParent().text
    return int(re.findall(r'\d+', beds_span)[0])


def baths(mc):
    summary_bar = mc.find('div', class_='summarybar')
    baths_span = summary_bar.find(string=re.compile('Bath')).findParent().text
    return int(re.findall(r'\d+', baths_span)[0])


def description(mc):
    return mc.find('div', itemprop='description').text.strip()


def features_list(mc):
    feature_table = soup.find('caption', string=re.compile('Special'))
    return feature_table.findNext('th').findNext('td').text.strip()


def property_type(mc):
    row = mc.find('th', string=re.compile('Property Type'))
    return row.parent.find('td').text.strip()


def property_overview(mc):
    """Dumps the property overview table to a dictionary"""
    property_overview = soup.find('caption', string=re.compile('Property Overview')).findParent()
    property_overview_dict = {}
    for row in property_overview.find_all("tr"):
        key = row.find('th').text.strip()
        val = row.find('td').text.strip()
        property_overview_dict[key] = val

    return property_overview_dict


if __name__ == "__main__":

    # save target to local file so it doesn't change on us.
    fpath = '../examples/R2227563.html'

    # load from file
    with open(fpath, 'r') as fp:
        page = fp.read()
    soup = BeautifulSoup(page, 'html5lib')

    param = property_type(soup)
    print('Condo' in param)


