from math import ceil
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from . import constants as const
from ..views import POSTS_PER_PAGE

add_post_count = ceil(POSTS_PER_PAGE / 2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.group = const.create_test_group()
        for i in range(POSTS_PER_PAGE + add_post_count):
            post = const.create_test_post(cls.user, cls.group)
            setattr(cls, f"post{i}", post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_posts_pagination(self):
        urls = {
            'home_first': reverse('posts:home'),
            'home_second': reverse('posts:home') + '?page=2',
            'group_list_first': reverse('posts:group_list',
                                        args=[self.group.slug]),
            'group_list_second': reverse('posts:group_list',
                                         args=[self.group.slug]) + '?page=2',
            'profile_first': reverse('posts:profile',
                                     args=[self.user.username]),
            'profile_second': reverse('posts:profile',
                                      args=[self.user.username]) + '?page=2',

        }
        expected_posts_counts = {
            'home_first': POSTS_PER_PAGE,
            'home_second': add_post_count,
            'group_list_first': POSTS_PER_PAGE,
            'group_list_second': add_post_count,
            'profile_first': POSTS_PER_PAGE,
            'profile_second': add_post_count,
        }

        for name, url in urls.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                expected_count = expected_posts_counts[name]
                real_count = len(response.context['page_obj'])
                self.assertEqual(real_count, expected_count)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_user(cls.user)
        const.delete_test_group(cls.group)
