# from django.test import TestCase, Client
# from django.contrib.auth import get_user_model
# from http import HTTPStatus


# User = get_user_model()


# class PostURLTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create_user(
#             username="user",
#             email="test@yandex.ru",
#             password="123"
#         )

#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)

#     def test_guest_client_urls_status_code(self):
#         """Проверка status_code для неавторизованного пользователя"""
#         url_code = {
#             "/auth/logout/": HTTPStatus.OK,
#             "/auth/signup/": HTTPStatus.OK,
#             "/auth/login/": HTTPStatus.OK,
#             "/auth/password_change/": HTTPStatus.FOUND,
#             "/auth/password_change/done/": HTTPStatus.FOUND,
#             "/auth/password_reset/": HTTPStatus.OK,
#             "/auth/password_reset/done/": HTTPStatus.OK,
#             "/auth/reset/<uidb64>/<token>/": HTTPStatus.OK,
#             "/auth/reset/done/": HTTPStatus.OK,
#             "/auth/unexisting_page/": HTTPStatus.NOT_FOUND,
#         }
#         for url, code in url_code.items():
#             with self.subTest(url=url):
#                 response = self.guest_client.get(url)
#                 self.assertEqual(response.status_code, code)

#     def test_authorized_client_urls_status_code(self):
#         """Проверка status_code для авторизованного пользователя"""
#         url_code = {
#             "/auth/logout/": HTTPStatus.OK,
#             "/auth/signup/": HTTPStatus.OK,
#             "/auth/login/": HTTPStatus.OK,
#             "/auth/password_change/": HTTPStatus.FOUND,
#             "/auth/password_change/done/": HTTPStatus.FOUND,
#             "/auth/password_reset/": HTTPStatus.OK,
#             "/auth/password_reset/done/": HTTPStatus.OK,
#             "/auth/reset/<uidb64>/<token>/": HTTPStatus.OK,
#             "/auth/reset/done/": HTTPStatus.OK,
#             "/auth/unexisting_page/": HTTPStatus.NOT_FOUND,
#         }
#         for url, code in url_code.items():
#             with self.subTest(url=url):
#                 response = self.authorized_client.get(url)
#                 self.assertEqual(response.status_code, code)

#     def test_urls_uses_correct_template(self):
#         """Проверка на соответствие URL-адресса и шаблона"""
#         url_template = {
#             "/auth/logout/": "users/logged_out.html",
#             "/auth/signup/": "users/signup.html",
#             "/auth/login/": "users/login.html",
#             "/auth/password_change/": "users/password_change_form.html",
#             "/auth/password_change/done/": "users/password_change_done.html",
#             "/auth/password_reset/": "users/password_reset_form.html",
#             "/auth/password_reset/done/": "users/password_reset_done.html",
#             "/auth/reset/<uidb64>/<token>/": "users/password_reset_confirm.html",
#             "/auth/reset/done/": "users/password_reset_complete.html",
#         }
#         for url, template in url_template.items():
#             with self.subTest(url=url):
#                 response = self.authorized_client.get(url)
#                 self.assertTemplateUsed(response, template)
