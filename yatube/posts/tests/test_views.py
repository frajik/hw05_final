from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Post, Group, Follow
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.auth = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.authorized_client = Client()
        self.author_client.force_login(PostViewsTests.post.author)
        self.authorized_client.force_login(PostViewsTests.auth)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_cache_index(self):
        """Проверка работы кэша на главной странице"""
        post = Post.objects.create(
            text="Тестовый пост для проверки кэша",
            author=self.author
        )
        add_content = self.author_client.get(
            reverse("posts:index")
        ).content
        post.delete()
        delete_content = self.author_client.get(
            reverse("posts:index")
        ).content
        self.assertEqual(add_content, delete_content)
        cache.clear()
        cache_clear_content = self.author_client.get(
            reverse("posts:index")
        ).content
        self.assertNotEqual(add_content, cache_clear_content)

    def test_pages_uses_correct_template_for_auth_client(self):
        """URL-адрес использует соответствующий шаблон."""
        name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={
                "slug": PostViewsTests.group.slug
            }): "posts/group_list.html",
            reverse("posts:profile", kwargs={
                "username": PostViewsTests.author.username
            }): "posts/profile.html",
            reverse("posts:post_detail", kwargs={
                "post_id": PostViewsTests.post.id
            }): "posts/post_detail.html",
            reverse("posts:post_edit", kwargs={
                "post_id": PostViewsTests.post.id
            }): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for name, template in name_template.items():
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_guest_client(self):
        """URL-адрес использует соответствующий шаблон."""
        name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={
                "slug": PostViewsTests.group.slug
            }): "posts/group_list.html",
            reverse("posts:profile", kwargs={
                "username": PostViewsTests.author.username
            }): "posts/profile.html",
            reverse("posts:post_detail", kwargs={
                "post_id": PostViewsTests.post.id
            }): "posts/post_detail.html",
        }
        for name, template in name_template.items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        names = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={
                "slug": PostViewsTests.group.slug
            }),
            reverse("posts:profile", kwargs={
                "username": PostViewsTests.author.username
            }),
        ]
        for name in names:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                first_object = response.context["page_obj"][0]
                post_author = first_object.author.username
                post_text = first_object.text
                post_group = first_object.group.title
                post_image = first_object.image
                self.assertEqual(post_author, "author")
                self.assertEqual(post_text, "Тестовый пост")
                self.assertEqual(post_group, "Тестовая группа")
                self.assertEqual(post_image, self.post.image)

    def text_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстомю"""
        response = (self.author_client.get(
            reverse("posts:post_detail", kwargs={
                "post_id": PostViewsTests.post.id
            })))
        self.assertEqual(
            response.context.get("group").title, "author"
        )
        self.assertEqual(
            response.context.get("post").text, "Тестовый пост"
        )
        self.assertEqual(
            response.context.get("group").slug, "test-slug"
        )
        self.assertEqual(
            response.context.get("post").image, self.post.image
        )

    def test_pages_with_forms_show_correct_context(self):
        """Шаблоны с формой сформированы с правильным контекстом."""
        names = [
            reverse("posts:post_create"),
            reverse("posts:post_edit", kwargs={
                "post_id": PostViewsTests.post.id
            }),
        ]
        for name in names:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIsInstance(
                    response.context["form"].fields["text"],
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    response.context["form"].fields["group"],
                    forms.fields.ChoiceField
                )
                self.assertIsInstance(
                    response.context["form"].fields["image"],
                    forms.fields.ImageField
                )

    def test_follow_author(self):
        """Проверка подписки на автора"""
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author}
            )
        )
        follow = Follow.objects.all().latest("id")
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(follow.author_id, self.author.id)
        self.assertEqual(follow.user_id, self.auth.id)

    def test_unfollow_author(self):
        """Проверка отписки от автора"""
        Follow.objects.create(
            user=self.auth,
            author=self.author
        )
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_author_posts(self):
        """Проверка появления нового поста для тех, кто подписан"""
        Follow.objects.create(
            user=self.auth,
            author=self.author
        )
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        self.assertIn(self.post, response.context["page_obj"].object_list)

    def test_unfollow_author_posts(self):
        """Проверка появления поста для тех, кто не подписан"""
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn(self.post, response.context["page_obj"].object_list)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="author")
        cls.group = Group.objects.create(
            title="Тестовая  группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        Post.objects.bulk_create(
            [Post(
                text=f"Тестовый пост #{i}",
                author=cls.author,
                group=cls.group
            ) for i in range(13)]
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.author.username
            }),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = len(self.guest_client.get(
                    page).context.get('page_obj'))
                self.assertEqual(
                    response,
                    posts_on_first_page
                )
                response = len(self.guest_client.get(
                    page + '?page=2').context.get('page_obj'))
                self.assertEqual(
                    response,
                    posts_on_second_page
                )
