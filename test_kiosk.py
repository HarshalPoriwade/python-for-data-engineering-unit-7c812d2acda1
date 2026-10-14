import contextlib
import io
import os
import tempfile
import unittest

import kiosk


class KioskTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = temp.name
        self.rates = {"EUR": 1.08, "GBP": 1.27}

    def test_convert_eur_250(self):
        self.assertEqual(kiosk.convert(250, 1.08), 270.00)

    def test_receipt_has_all_four_values(self):
        receipt = kiosk.make_receipt("EUR", "250", self.rates)
        self.assertEqual(receipt, {"code": "EUR", "amount": 250.0,
                                   "rate": 1.08, "usd_total": 270.0})

    def test_lowercase_code_is_accepted(self):
        receipt = kiosk.make_receipt("gbp", "100", self.rates)
        self.assertEqual(receipt["usd_total"], 127.0)

    def test_unknown_code_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            kiosk.make_receipt("XYZ", "250", self.rates)
        self.assertIn("Unknown currency code: XYZ", str(caught.exception))

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            kiosk.make_receipt("EUR", "-50", self.rates)
        self.assertIn("positive", str(caught.exception))

    def test_zero_and_text_amounts_are_rejected(self):
        for bad in ["0", "abc", "nan", "inf"]:
            with self.assertRaises(ValueError):
                kiosk.parse_amount(bad)

    def test_load_rates_handles_windows_line_endings(self):
        path = os.path.join(self.folder, "rates.txt")
        with open(path, "w", newline="") as file:
            file.write("EUR=1.08\r\nGBP=1.27\r\n\r\n")
        self.assertEqual(kiosk.load_rates(path), {"EUR": 1.08, "GBP": 1.27})

    def test_code_without_amount_is_rejected(self):
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            result = kiosk.main(["GBP"])
        self.assertEqual(result, 1)
        self.assertIn("type a code and an amount", printed.getvalue())

    def test_receipt_survives_save_and_load(self):
        path = os.path.join(self.folder, "receipt.json")
        receipt = kiosk.make_receipt("EUR", "250", self.rates)
        kiosk.save_receipt(receipt, path)
        self.assertEqual(kiosk.load_receipt(path), receipt)


if __name__ == "__main__":
    unittest.main()