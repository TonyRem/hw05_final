from django.test import TestCase
from django.core.cache import cache

from ..models import NUM_CHARS_POST_STR
from . import constants as const


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.group = const.create_test_group()
        cls.post = const.create_test_post(cls.user)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_group_str = group.title
        self.assertEqual(expected_group_str, str(group))

        post = PostModelTest.post
        expected_post_str = post.text[:NUM_CHARS_POST_STR]
        self.assertEqual(expected_post_str, str(post))
        cache.clear()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_group(cls.group)
        const.delete_test_user(cls.user)
