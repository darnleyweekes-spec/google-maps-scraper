import unittest
from unittest.mock import patch

import official_sites


class ResearchTests(unittest.TestCase):
    def test_records_public_email_source_and_ignores_script(self):
        page = '<script>fake@example.com</script><p>hello@studio.example</p><a href="/contact">Contact</a><a href="https://other.example/contact">Other</a>'
        with patch.object(official_sites, 'fetch', return_value=(page, 'https://studio.example/')), patch.object(official_sites.time, 'sleep'):
            result = official_sites.research('Studio', 'https://studio.example/', 2)
        self.assertEqual(set(result['emails']), {'hello@studio.example'})
        self.assertEqual(result['status'], 'read')
        self.assertFalse(result['delivery_verified'])
        self.assertFalse(result['purchase_intent_verified'])

    def test_failure_does_not_infer_contacts(self):
        with patch.object(official_sites, 'fetch', side_effect=TimeoutError('blocked')):
            result = official_sites.research('Studio', 'https://studio.example/')
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['emails'], {})
        self.assertEqual(result['errors'][0]['error'], 'blocked')


if __name__ == '__main__':
    unittest.main()
