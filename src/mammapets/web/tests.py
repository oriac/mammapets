from django.test import TestCase
from django.urls import reverse

class HomePageTests(TestCase):
    def test_home_page_status_code(self):
        """Test that the home page returns a 200 OK status code."""
        response = self.client.get(reverse('web:index'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that the home page renders the correct template."""
        response = self.client.get(reverse('web:index'))
        self.assertTemplateUsed(response, 'pets/index.html')

    def test_contract_page_status_code(self):
        """Test that the contract page returns a 200 OK status code."""
        response = self.client.get(reverse('web:contract'))
        self.assertEqual(response.status_code, 200)

    def test_contract_page_uses_correct_template(self):
        """Test that the contract page renders the correct template."""
        response = self.client.get(reverse('web:contract'))
        self.assertTemplateUsed(response, 'pets/contract.html')
