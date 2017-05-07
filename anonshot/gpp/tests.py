from django.test import TestCase

from django.core.urlresolvers import resolve
from django.test import TestCase
from gpp.views import home_page, upload

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')  #2
        self.assertEqual(found.func, home_page)  #3

    def test_resolves_upload_url_view(self):
        found = resolve('/upload/')  #2
        self.assertEqual(found.func, upload)  #3
