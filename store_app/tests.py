from django.test import TestCase
from django.urls import reverse


class PublicPageTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "走進店裡")
        self.assertContains(response, "Dunk Low")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "兩秒完成登入")

    def test_member_pages_require_login(self):
        response = self.client.get(reverse("shopping"))
        self.assertRedirects(response, reverse("login"))
