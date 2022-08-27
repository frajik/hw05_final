from http import HTTPStatus
from django.test import TestCase, Client, override_settings
from ..models import Post, Group, Comment
from ..forms import PostForm
from django.urls import reverse
from django.contrib.auth import get_user_model
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
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
        cls.form = PostForm

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.post.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_for_guest_client(self):
        """Валидная форма создает запись в Post"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост",
            "group": self.group.id,
            "image": self.post.image,
        }
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertTemplateUsed(
            response, "users/login.html"
        )
        self.assertEqual(
            Post.objects.count(),
            post_count
        )

    def test_create_post_for_auth_client(self):
        """Валидная форма создает запись в Post"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост",
            "group": self.group.id,
            "image": self.post.image
        }
        response = self.author_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={'username': self.author.username})
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=form_data["group"],
                image=form_data["image"]

            ).exists
        )

    def test_post_edit_for_guest_client(self):
        """Валидная форма изменяет запись в БД"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост2",
            "group": self.group.id,
            "image": self.post.image
        }
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs={
                "post_id": PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTemplateUsed(
            response, "users/login.html"
        )
        self.assertEqual(
            Post.objects.count(),
            post_count
        )

    def test_post_edit_for_auth_client(self):
        """Валидная форма изменяет запись в БД"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост2",
            "group": self.group.id,
            "image": self.post.image
        }
        response = self.author_client.post(
            reverse("posts:post_edit", kwargs={
                "post_id": PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            post_count
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=form_data["group"],
                image=form_data["image"]
            ).exists
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_comments_for_auth_client(self):
        """Комментирование поста авторизированным пользователем."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text="Тестовый текст поста",
            author=self.author
        )
        form_data = {"text": "Тестовый комментарийй"}
        response = self.author_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data["text"],
                author=self.author,
                post_id=post.id
            )
        )
        self.assertEqual(
            Comment.objects.count(), comments_count + 1
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", args={post.id})
        )

    def test_post_comments_for_guest_client(self):
        """Комментирование поста неавторизированным пользователем."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text="Тестовый текст поста",
            author=self.author
        )
        form_data = {"text": "Тестовый комментарийй"}
        response = self.guest_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Comment.objects.count(), comments_count
        )
        self.assertRedirects(
            response, reverse("login") + '?next=' + reverse(
                "posts:add_comment", kwargs={"post_id": post.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
