from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Follow, Post
from . import constants as const


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.another_user = const.create_test_user('Another')
        cls.not_follow_user = const.create_test_user('NotFollow')
        cls.post = const.create_test_post(cls.another_user)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_follow_client = Client()
        self.not_follow_client.force_login(self.not_follow_user)
        cache.clear()

    def test_follow(self):
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                    'username': self.another_user.username})
        )

        # Проверяем, что пользователь успешно подписался на другого пользователя
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.another_user).exists())

        # Проверяем, что посты пользователя появились на странице подписок
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertContains(response, self.post.text)

        # Создаем еще один пост и проверяем, что он появился на странице
        # подписок у подписанного пользователя и не появился у неподписанного
        another_post = Post.objects.create(
            author=self.another_user,
            text='Тест появления поста на странице фолловера'
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertContains(response, another_post.text)

        response = self.not_follow_client.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, another_post.text)
