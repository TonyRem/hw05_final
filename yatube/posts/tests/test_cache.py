from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from time import sleep

from . import constants as const
from .. views import CACH_TIME


class IndexViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.post = const.create_test_post(cls.user)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache(self):
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertContains(response, self.post.text)

        self.post.delete()
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertContains(response, self.post.text)

        sleep(CACH_TIME)
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertNotContains(response, self.post.text)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_user(cls.user)
