import extractors
import logging


class Listing:

    @staticmethod
    def factory(url):
        soup = extractors.Ladle.get_soup(url)
        type = extractors.property_type(soup)

        if 'Apt' in type:
            return Apartment(soup)
        elif 'Townhouse' in type:
            return Townhouse(soup)
        elif 'House' in type:
            return House(soup)
        elif 'plex' in type:
            return Nplex(soup)
        elif 'Land' in type:
            return Land(soup)
        else:
            raise AssertionError('Type "{}" not recognized'.format(type))


class Apartment(Listing):

    def __init__(self, soup):
        pass


class House(Listing):

    def __init__(self, soup):
        pass


class Townhouse(Listing):

    def __init__(self, soup):
        pass


class Nplex(Listing):

    def __init__(self, soup):
        pass


class Land(Listing):

    def __init__(self, soup):
        pass


if __name__ == "__main__":

    l = Listing.factory('https://www.rew.ca/properties/R2239609/2875-w-6-avenue-vancouver-bc')
    print(type(l))
