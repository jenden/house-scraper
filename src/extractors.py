import re
import requests
from numpy.random import exponential
import time
from log import logger
from bs4 import BeautifulSoup
import json
from decimal import Decimal
import gzip

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
    __random_time = lambda: exponential(1, 1)[0]

    @staticmethod
    def get_soup(url):
        timeout = Ladle.__random_time()
        if Ladle.__last_request + timeout > time.time():
            time.sleep(timeout)

        logger.info('Requested url: {} after {:.1f}s delay'.format(url, timeout))
        return get_page_soup(url)


def listing_id_from_url(url):
    return re.findall('(?<=properties/).*(?=/)', url)[0]


def listing_id_from_head(soup):
    """Returns the listing id from the html head"""
    import re
    url = soup.head.link['href']
    return listing_id_from_url(url)


def main_content(soup):
    """Returns the section in the page which contains the listing"""
    return soup.find('section', class_='container maincontentspacer')


# fields contained in the property header
def property_header(mc):
    return mc.find('div', class_='propertyheader')


def street_address(ph):
    return ph.find('span', itemprop='streetAddress').text.strip()


def city(ph):
    return ph.find('span', itemprop='addressLocality').text.strip()


def province(ph):
    return ph.find('span', itemprop='addressRegion').text.strip()


def postal_code(ph):
    return ph.find('span', itemprop='postalCode').text.strip()


def listing_id_from_property_header(ph):
    id_string = ph.find('li', string=re.compile('Listing ID')).text
    return re.compile(r'R\d+').findall(id_string)[0]


def list_price(ph):
    price = ph.find('div', class_='propertyheader-price').text.strip()
    return price_str_to_int(price)


def price_str_to_int(price):
    return int(price.strip('$').replace(',', ''))


# fields contained in the summary bar
def summary_bar(mc):
    return mc.find('div', class_='summarybar')


def beds(sb):
    beds_span = sb.find(string=re.compile('Bed')).findParent().text
    return int(re.findall(r'\d+', beds_span)[0])


def baths(sb):
    baths_span = sb.find(string=re.compile('Bath')).findParent().text
    return int(re.findall(r'\d+', baths_span)[0])


def square_footage(sb):
    sqft_span = sb.find(string=re.compile('Sqft')).findParent().text
    return int(re.findall(r'\d+', sqft_span)[0])


def property_type_from_summary_bar(sb):
    span = sb.find('div', string=re.compile('Type')).findParent()
    return span.text.replace('Type', '').strip()


# property description
def description(mc):
    div = mc.find('div', itemprop='description')
    return div.text.strip()


# other sections
def property_type_from_table(mc):
    row = mc.find('th', string=re.compile('Property Type'))
    return row.parent.find('td').text.strip()


def property_overview_table(mc):
    """Dumps the property overview table to a dictionary"""
    table = mc.find('caption', string=re.compile('Property Overview'))
    if table is not None:
        return html_table_to_dict(table.findParent())


def features_table(mc):
    table = mc.find('caption', string=re.compile('Special'))
    if table is not None:
        return html_table_to_dict(table.findParent())


def building_information(mc):
    div = mc.find('div', class_='buildingoverview')
    if div is None:
        return
    building = {}
    building['name'] = div.header.a.text.strip()
    building['description'] = div.find('div', class_='buildingoverview-description').text
    table = div.find('div', class_='buildingoverview-table')
    for item in table.find_all('dl', class_='buildingoverview-attributes'):
        key = item.find('dt').text.replace(':', '').strip()
        value = item.find('dd').text.strip()
        building[key] = value
    return building


def nearby_schools(mc):
    school_list = mc.find('div', class_='detailslist', id='nearbySchools')
    if school_list is None:
        return
    schools = []
    for school_row in school_list.find_all('div', class_='detailslist-row'):
        schools.append(school_details(school_row))
    return schools


def school_details(school_row):
    a = school_row.find('div', class_='detailslist-row_cap').find('a')
    return json.loads(a['data-popup-map-marker-school'], parse_float=Decimal)


def html_table_to_dict(table_soup):
    table_dict = {}
    for row in table_soup.find_all("tr"):
        key = row.find('th').text.strip()
        val = row.find('td').text.strip()
        if key != '' and val != '':
            table_dict[key] = val
    return table_dict


def compress_html(soup):
    return {'format': 'gzip',
            'compression_level': 9,
            'format': 'binary',
            'data': gzip.compress(bytes(soup.prettify(), 'utf-8'), compresslevel=9)}


if __name__ == "__main__":

    # save target to local file so it doesn't change on us.
    fpath = '../examples/R2227563.html'

    # load from file
    with open(fpath, 'r') as fp:
        page = fp.read()
    soup = BeautifulSoup(page, 'html5lib')
    mc = main_content(soup)
    gz = compress_html(mc)
    import sys
    print(sys.getsizeof(mc.prettify()))
    print(sys.getsizeof(gz))

    html = gzip.decompress(gz['data'])
    print(html)





