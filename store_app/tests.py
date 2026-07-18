from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.template.loader import get_template
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


class TemplateCompilationTests(TestCase):
    def test_all_project_templates_compile(self):
        template_root = Path(settings.TEMPLATES[0]["DIRS"][0])
        template_files = sorted(template_root.rglob("*.html"))

        self.assertGreater(len(template_files), 0)
        for template_file in template_files:
            with self.subTest(template=template_file.name):
                get_template(template_file.relative_to(template_root).as_posix())
