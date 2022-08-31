from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group, Comment, Follow
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.user = User.objects.create_user(username="user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text="Тестовый комментарий",
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(PostURLTests.post.author)
        cache.clear()

    def test_guest_client_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя"""
        url_code = {
            "/": HTTPStatus.OK,
            f"/group/{PostURLTests.post.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostURLTests.user}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/edit/": HTTPStatus.FOUND,
            f"/posts/{PostURLTests.post.id}/comment/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.user}/follow/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.user}/unfollow/": HTTPStatus.FOUND,
            "/follow/": HTTPStatus.FOUND,
            "/create/": HTTPStatus.FOUND,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_authorized_client_urls_status_code(self):
        """Проверка status_code для авторизованного пользователя"""
        url_code = {
            "/": HTTPStatus.OK,
            f"/group/{PostURLTests.post.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostURLTests.user}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/edit/": HTTPStatus.FOUND,
            f"/posts/{PostURLTests.post.id}/comment/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.author}/follow/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.author}/unfollow/": HTTPStatus.FOUND,
            "/follow/": HTTPStatus.OK,
            "/create/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_author_client_urls_status_code(self):
        """Проверка status_code для автора поста"""
        url_code = {
            "/": HTTPStatus.OK,
            f"/group/{PostURLTests.post.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostURLTests.user}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/edit/": HTTPStatus.OK,
            f"/posts/{PostURLTests.post.id}/comment/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.author}/follow/": HTTPStatus.FOUND,
            f"/profile/{PostURLTests.author}/unfollow/": HTTPStatus.NOT_FOUND,
            "/follow/": HTTPStatus.OK,
            "/create/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """Проверка на соответствие URL-адресса и шаблона"""
        url_template = {
            "/": "posts/index.html",
            f"/group/{PostURLTests.post.group.slug}/": "posts/group_list.html",
            f"/profile/{PostURLTests.user}/": "posts/profile.html",
            f"/posts/{PostURLTests.post.id}/": "posts/post_detail.html",
            f"/posts/{PostURLTests.post.id}/edit/": "posts/create_post.html",
            "/follow/": "posts/follow.html",
            "/create/": "posts/create_post.html",
        }
        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
