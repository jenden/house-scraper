import unittest
from bs4 import BeautifulSoup
import extractors


class ExtractorTests(unittest.TestCase):

    def setUp(self):

        # load page from file
        fpath = '../examples/R2227563.html'
        with open(fpath, 'r') as fp:
            page = fp.read()

        self.soup = BeautifulSoup(page, 'html5lib')
        self.mc = extractors.main_content(self.soup)
        self.ph = extractors.property_header(self.mc)

    def test_street_address(self):
        actual = extractors.street_address(self.ph)
        self.assertEqual(actual, '401 E 55th Avenue')

    def test_listing_id_from_head(self):
        actual = extractors.listing_id_from_head(self.soup)
        self.assertEqual(actual, 'R2227563')


if __name__ == '__main__':
    unittest.main()