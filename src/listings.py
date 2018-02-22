import extractors
from log import logger
from collections import OrderedDict
from database import ExtractTable
from datetime import datetime


class Listing:

    def __init__(self, listing_id, soup):
        self.id = listing_id
        self.soup = soup
        self.details = OrderedDict()
        self.parse()

    @staticmethod
    def factory(url):
        soup = extractors.Ladle.get_soup(url)
        listing_id = extractors.listing_id_from_url(url)
        listing_type = extractors.property_type_from_table(soup)

        logger.info('Parsing {} {}'.format(listing_type, listing_id))

        if 'Apt' in listing_type:
            return Apartment(listing_id, soup)
        elif 'Townhouse' in listing_type:
            return Townhouse(listing_id, soup)
        elif 'House' in listing_type:
            return House(listing_id, soup)
        elif 'plex' in listing_type:
            return Nplex(listing_id, soup)
        elif 'Land' in listing_type:
            return Land(listing_id, soup)
        else:
            logger.error('Type "{}" not recognized in listing {}'.format(listing_type, listing_id))
            return

    def extract(self, extractor_function, soup, field_name=None):
        try:
            extract = extractor_function(soup)
        except (ValueError, AttributeError) as e:
            if soup is not None:
                html = soup.prettify().replace('\n', '')
                message = '{} not found in soup.'.format(extractor_function.__name__)
            else:
                message = 'No soup provided to {}. Check the previous extractor.'.format(extractor_function.__name__)
            logger.error('Listing {}, Error: {}. '.format(self.id, str(e)) + message)
            return

        if extract is None or extract == "":
            return
        elif field_name is not None:
            self.details[field_name] = extract
        else:
            return extract

    def parse(self):
        self.details['ListingID'] = self.id
        self.details['ExtractTime'] = datetime.now().isoformat()

        mc = self.extract(extractors.main_content, self.soup)

        ph = self.extract(extractors.property_header, mc)
        self.extract(extractors.list_price, ph, 'ListPrice')
        self.extract(extractors.street_address, ph, 'StreetAddress')
        self.extract(extractors.city, ph, 'City')
        self.extract(extractors.province, ph, 'Province')
        self.extract(extractors.postal_code, ph, 'PostalCode')

        sb = self.extract(extractors.summary_bar, mc)
        self.extract(extractors.beds, sb, 'Beds')
        self.extract(extractors.baths, sb, 'Baths')
        self.extract(extractors.square_footage, sb, 'Sqft')
        self.extract(extractors.property_type_from_summary_bar, sb, 'Type')

        self.extract(extractors.description, mc, 'Description')

        self.extract(extractors.property_overview_table, mc, 'PropertyOverviewTable')
        self.extract(extractors.features_table, mc, 'FeatureTable')
        self.extract(extractors.nearby_schools, mc, 'NearbySchools')

        self.details['CompressedHTML'] = extractors.compress_html(mc)

    def write_to_db(self):
        # print(self.details)
        ExtractTable.put_item(Item=self.details)


class Apartment(Listing):

    def __init__(self, listing_id, soup):
        super().__init__(listing_id, soup)
        self.extract(extractors.building_information, soup, 'BuildingInfo')
        self.write_to_db()


class House(Listing):

    def __init__(self, listing_id, soup):
        super().__init__(listing_id, soup)
        self.write_to_db()


class Townhouse(Listing):

    def __init__(self, listing_id, soup):
        super().__init__(listing_id, soup)
        self.write_to_db()


class Nplex(Listing):

    def __init__(self, listing_id, soup):
        super().__init__(listing_id, soup)
        self.write_to_db()


class Land(Listing):

    def __init__(self, listing_id, soup):
        super().__init__(listing_id, soup)
        self.write_to_db()


if __name__ == "__main__":

    l = Listing.factory('https://www.rew.ca/properties/R2239609/2875-w-6-avenue-vancouver-bc')
    print(type(l))
