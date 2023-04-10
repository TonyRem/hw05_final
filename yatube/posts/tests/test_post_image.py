from django.test import TestCase, Client
from django.urls import reverse
from django.db.models.fields.files import ImageFieldFile
from django.core.cache import cache

from . import constants as const


class TaskViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = const.create_test_user()
        cls.group = const.create_test_group()
        cls.image = const.create_test_image()
        cls.post = const.create_test_post(
            cls.author, cls.group, cls.image
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_post_image_context(self):
        """Проверяет наличие переданной картинки на всех страницах с постом"""
        # Post detail page
        response = self.authorized_client.get(reverse(viewname='posts:post_detail',
                                                      args=[self.post.id]))
        actual_image = response.context['post'].image
        expected_image = self.post.image

        actual_image_content = actual_image.read()
        expected_image_content = expected_image.read()

        self.assertIsNotNone(actual_image_content)
        self.assertIsInstance(actual_image, ImageFieldFile)
        self.assertEqual(actual_image_content, expected_image_content)

        # Home page posts
        response = self.authorized_client.get(reverse('posts:home'))
        post_image = response.context['page_obj'][0].image
        image_content = post_image.read()

        self.assertIsNotNone(image_content)
        self.assertIsInstance(post_image, ImageFieldFile)
        self.assertEqual(image_content, expected_image_content)

        # Profile page posts
        response = self.authorized_client.get(reverse(viewname='posts:profile',
                                                      args=[self.author.username]))
        post_image = response.context['page_obj'][0].image
        image_content = post_image.read()

        self.assertIsNotNone(image_content)
        self.assertIsInstance(post_image, ImageFieldFile)
        self.assertEqual(image_content, expected_image_content)

        # Group page posts
        response = self.authorized_client.get(reverse(viewname='posts:group_list',
                                                      args=[self.group.slug]))
        post_image = response.context['page_obj'][0].image
        image_content = post_image.read()

        self.assertIsNotNone(image_content)
        self.assertIsInstance(post_image, ImageFieldFile)
        self.assertEqual(image_content, expected_image_content)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_user(cls.author)
        const.delete_test_group(cls.group)
        cache.clear()
