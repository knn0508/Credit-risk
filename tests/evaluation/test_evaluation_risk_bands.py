import math
import unittest

from src.evaluation.risk_bands import band, bands


class TestBand(unittest.TestCase):
    def test_boundaries_inclusive_upper(self):
        self.assertEqual(band(0.05, 0.05, 0.15), "Low")
        self.assertEqual(band(0.0501, 0.05, 0.15), "Medium")
        self.assertEqual(band(0.15, 0.05, 0.15), "Medium")
        self.assertEqual(band(0.1501, 0.05, 0.15), "High")

    def test_extremes(self):
        self.assertEqual(band(0.0, 0.05, 0.15), "Low")
        self.assertEqual(band(1.0, 0.05, 0.15), "High")

    def test_invalid_p(self):
        for p in (-0.1, 1.1, math.nan, None):
            with self.assertRaises(ValueError):
                band(p, 0.05, 0.15)

    def test_invalid_thresholds(self):
        for lo, hi in ((None, None), (0.2, 0.1), (0.1, 0.1), (0.1, 1.5)):
            with self.assertRaises(ValueError):
                band(0.1, lo, hi)

    def test_bands_list(self):
        self.assertEqual(bands([0.01, 0.1, 0.5], 0.05, 0.15), ["Low", "Medium", "High"])


if __name__ == "__main__":
    unittest.main()
