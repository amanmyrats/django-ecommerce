from django.test import TestCase
from django.urls import reverse

from ecommerce import views


class HomePageTests(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        
    def test_view_url_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_correct_html(self):
        response = self.client.get('/en/')
        self.assertContains(response, 'Popular products')

    def test_home_page_does_not_contain_incorrect_html(self):
        response = self.client.get('/en/')
        self.assertNotContains(response, '404')
