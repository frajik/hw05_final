from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
set_limit = 15


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост"
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True
    )

    def __str__(self):
        return self.text[:set_limit]

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Автор комментария"
    )
    text = models.TextField(
        verbose_name="Текст комментария"
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан"
    )

    def __str__(self):
        return self.text[:set_limit]

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="user_author",
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
