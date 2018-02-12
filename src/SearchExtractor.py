from bs4 import BeautifulSoup
import requests
import re

import logging
logging.basicConfig(level=logging.INFO)


class AreaListing:
    BASE_URL = 'https://www.rew.ca'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) '
                             'Version/7.0.3 Safari/7046A194A'}

    def __init__(self, area_listing_url):
        self.area_listing_url = area_listing_url
        self.listings = set()
        self.update()

    def _get_page_soup(self, url):
        # sometimes links are relative, add base when needed
        if not url.startswith('https://'):
            url = self.BASE_URL + url
        page = requests.get(url, headers=self.HEADERS)
        return BeautifulSoup(page.text, 'html5lib')

    def update(self):
        self.soup = self._get_page_soup(self.area_listing_url)

        # REW only lists 25 pages of 20 listings. If there are more than 500 listings then we need to a
        # set of filters we can iterate over and collect listings in each area

        try:
            pagination_string = self.soup.find('div', class_='paginationlinks-caption').text
            matches = re.findall(r'(?<=of )\d+', pagination_string)
            num_listings = int(matches[0])
        except:
            logging.error('Number of results not found in pagination string: {}'.format(pagination_string))
            num_listings = 0

        if num_listings < 500:
            # all listings accessible from this page
            self._crawl_search_results()
        else:
            # not all listings accessible from this page
            subarea_urls = self._find_subareas()

            for url in subarea_urls:
                self._crawl_search_results(url)
                logging.info('Total listings collected: {}'.format(len(self.listings)))


    def _find_subareas(self):
        subarea_lists = self.soup.find_all('ul', class_='list-unstyled subarealist')
        subarea_urls = {}

        for list_panel in subarea_lists:
            list_items = list_panel.find_all('a', class_='subarealist-item')
            [subarea_urls.update({subarea.text: subarea['href']}) for subarea in list_items]

        # sometimes the first few links are to the Area All (###) or Area East All (##), etc.
        # remove the areas which end with All immediately before the number of listings
        re_all = re.compile(r' All (?=\(\d+\))')
        return [value for key, value in subarea_urls.items() if re_all.search(key) is None]


    def _crawl_search_results(self, url=None):
        if url:
            soup = self._get_page_soup(url)
        else:
            soup = self.soup
            url = self.area_listing_url

        logging.info('Extracting from {}'.format(url))

        listing_urls = self._extract_listings(soup)
        self.listings.update(listing_urls)

        # crawl the next page if it exists
        next_page = soup.find('div', class_='paginationlinks').find('a', rel='next')
        if next_page:
            next_page_url = next_page['href']
            self._crawl_search_results(next_page_url)


    def _extract_listings(self, soup):
        url_extractor = lambda div: 'https://www.rew.ca' + div.find('span', class_='listing-address').find('a')['href']

        listings = soup.find('div', class_='organiclistings').find_all('div', class_='row listing-row')
        listing_urls = [url_extractor(listing) for listing in listings]
        return listing_urls






if __name__ == "__main__":

    url = 'https://www.rew.ca/properties/areas/vancouver-bc'
    alp = AreaListing(url)
    alp.listings

