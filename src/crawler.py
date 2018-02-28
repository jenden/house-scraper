import re
from datetime import datetime
from dateutil import parser as datetime_parser
import extractors
from listings import Listing
from database import ListingTable, Key
from log import logger


class Crawler:

    areas = set()

    def __init__(self, *args):
        [self.add_area(area_listing_url) for area_listing_url in list(args)]

    def add_area(self, area_listing_url):
        self.areas.add(AreaCrawler(area_listing_url))

    def update(self):
        for area in self.areas:
            logger.info('Scraping {}'.format(area))
            area.update()


class AreaCrawler:

    def __init__(self, area_listing_url, update=False):
        self.area_listing_url = area_listing_url
        self.area = area_listing_url.split('areas/')[-1].upper()
        self.listings = set()
        if update:
            self.update()

    def update(self):
        soup = extractors.Ladle.get_soup(self.area_listing_url)

        # REW only lists 25 pages of 20 listings. If there are more than 500 listings then we need to a
        # set of filters we can iterate over and collect listings in each area
        try:
            pagination_string = soup.find('div', class_='paginationlinks-caption').text
            matches = re.findall(r'(?<=of )\d+', pagination_string)
            num_listings = int(matches[0])
        except:
            logger.error('Number of results not found in pagination string: {}'.format(pagination_string))
            num_listings = 0

        if num_listings < 500:
            # all listings accessible from this page
            self._crawl_search_results(soup=soup)
        else:
            # not all listings accessible from this page
            subarea_urls = self._find_subareas(soup)

            for url in subarea_urls:
                self._crawl_search_results(url)

    def _find_subareas(self, soup):
        subarea_lists = soup.find_all('ul', class_='list-unstyled subarealist')
        subarea_urls = {}

        for list_panel in subarea_lists:
            list_items = list_panel.find_all('a', class_='subarealist-item')
            [subarea_urls.update({subarea.text: subarea['href']}) for subarea in list_items]

        # sometimes the first few links are to the 'Area All (21)' or 'Area East All (37)', etc.
        # remove the areas which end with All immediately before the number of listings
        re_all = re.compile(r' All (?=\(\d+\))')
        return [value for key, value in subarea_urls.items() if re_all.search(key) is None]


    def _crawl_search_results(self, url=None, soup=None):
        if url:
            soup = extractors.Ladle.get_soup(url)
        elif soup:
            url = self.area_listing_url
        else:
            raise AttributeError('You must supply a url or soup')

        logger.info('Extracting from {}'.format(url))
        self._find_listings(soup)

        # crawl the next page if it exists
        next_page = soup.find('div', class_='paginationlinks').find('a', rel='next')
        if next_page:
            next_page_url = next_page['href']
            self._crawl_search_results(next_page_url)

    def _find_listings(self, soup):
        listings = soup.find('div', class_='organiclistings').find_all('div', class_='row listing-row')
        [self._process_listing(listing) for listing in listings]

    def _process_listing(self, listing):
        url = listing.find('span', class_='listing-address').find('a')['href']
        listing_id = extractors.listing_id_from_url(url)
        price = extractors.price_str_to_int(listing.find('div', class_='listing-price').text)

        # check if data exists in table
        response = ListingTable.query(KeyConditionExpression=Key('ListingID').eq(listing_id))

        # if no, parse the linked page and add to extracts table
        if response['Count'] == 0:
            Listing.factory(url)
        # only save the record metadata if it was recorded on another day
        if response['Count'] > 0:
            record_datetime = datetime_parser.parse(response['Items'][-1]['DateTime'])
            record_date = datetime.date(record_datetime)
            if record_date == datetime.date(datetime.now()):
                logger.info('Already parsed {} on {}'.format(listing_id, record_date))
        else: # first time record, add the record to the listings table - allows tracking price changes and time on the market
            ListingTable.put_item(Item={
                'ListingID': listing_id,
                'DateTime': datetime.now().isoformat(),
                'Price': price,
                'URL': url})

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, AreaCrawler):
            return self.__repr__() == other.__repr__()

    def __repr__(self):
        return '<ListingArea:{}>'.format(self.area)


if __name__ == "__main__":

    c = Crawler('https://www.rew.ca/properties/areas/vancouver-bc',
                 'https://www.rew.ca/properties/areas/richmond-bc',
                 'https://www.rew.ca/properties/areas/burnaby-bc',
                 'https://www.rew.ca/properties/areas/new-westminster-bc',
                 'https://www.rew.ca/properties/areas/west-vancouver-bc',
                 'https://www.rew.ca/properties/areas/north-vancouver-bc')
    c.update()



