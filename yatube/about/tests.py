from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка status_code URL-адресса"""
        name_status = {
            reverse("about:author"): HTTPStatus.OK,
            reverse("about:tech"): HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND
        }
        for name, status in name_status.items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, status)

    def test_about_url_uses_correct_template(self):
        """Проверка на соответствие URL-адресса и шаблона"""
        name_template = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html"
        }
        for name, template in name_template.items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)
