class TestUnderConstructionView(SimpleTestCase):
    def test_page_resolves_successfully(self):
        response = self.client.get('/under-construction/')
        self.assertEqual(response.status_code, 200)
