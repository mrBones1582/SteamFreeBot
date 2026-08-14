import unittest
from unittest.mock import patch

from app import main


class DiscountEndTests(unittest.TestCase):
    def test_extracts_earliest_future_countdown(self):
        html = """
        <script>InitDailyDealTimer( $J('#a'), 2000000600 );</script>
        <script>InitDailyDealTimer( $J('#b'), 2000000300 );</script>
        """
        self.assertEqual(main._extract_discount_expiration_from_html(html, 2000000000), 2000000300)

    def test_ignores_past_countdown(self):
        html = "<script>InitDailyDealTimer($J('#a'), 1999990000);</script>"
        self.assertIsNone(main._extract_discount_expiration_from_html(html, 2000000000))

    def test_product_type(self):
        self.assertEqual(main._product_type({'type': 'game'}), 'game')
        self.assertEqual(main._product_type({'type': 'dlc'}), 'dlc')
        self.assertEqual(main._product_type({'type': 'music'}), 'other')


if __name__ == '__main__':
    unittest.main()
