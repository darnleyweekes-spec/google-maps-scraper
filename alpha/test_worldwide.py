import unittest

import worldwide


class QueryBatchTests(unittest.TestCase):
    def test_nationwide_catalog_covers_all_states_and_dc(self):
        locations = worldwide.NATIONWIDE
        self.assertGreaterEqual(len(locations), 100)
        for state in [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
            "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming", "District of Columbia",
        ]:
            self.assertTrue(any(state in location for location in locations), state)

    def test_nationwide_batches_are_bounded_and_continue_by_offset(self):
        first = worldwide.queries("agents", "nationwide", 0, 30)
        second = worldwide.queries("agents", "nationwide", 30, 30)
        self.assertEqual(len(first), 30)
        self.assertEqual(len(second), 30)
        self.assertNotEqual(set(first), set(second))
        self.assertTrue(all(" USA" in query for query in first + second))

    def test_worldwide_option_remains_available(self):
        result = worldwide.queries("learn", "worldwide", 0, 6)
        self.assertEqual(len(result), 6)
        self.assertTrue(any("Canada" in query or "UK" in query for query in result))


if __name__ == "__main__":
    unittest.main()
