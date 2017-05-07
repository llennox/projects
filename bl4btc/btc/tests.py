from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest 
from btc.views import home_page, faq_page, register_page, contact_page, sign_page
from btc.forms import RegistrationForm
from btc.models import Profil
from django.conf import settings


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)
 
    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(response.content.strip().endswith(b'</html>'))


    def test_faq_page_returns_correct_html(self):
        request = HttpRequest()
        response = faq_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(response.content.strip().endswith(b'</html>'))
#check for questions	

    def test_register_page_returns_correct_html(self):
        
        
        request = HttpRequest()
        response = register_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<form class="form-inline" action="/" method="post">', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))
#check that registry works includes email verification. . . later captcha

    def test_contact_page_returns_correct_html(self):
        request = HttpRequest()
        response = contact_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(response.content.strip().endswith(b'</html>'))
#check for contact details

        
    def test_sign_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(response.content.strip().endswith(b'</html>'))
#check that sign in works 
    

