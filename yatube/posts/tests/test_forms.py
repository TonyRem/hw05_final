from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Comment
from http import HTTPStatus
from django.core.cache import cache

from . import constants as const


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.group = const.create_test_group()
        cls.another_group = const.create_test_group('Другая тестовая группа',
                                                    'another-test-slug')
        cls.image = const.create_test_image()
        cls.post = const.create_test_post(cls.user, cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post_valid_form(self):
        """
        Тестирование формы создания поста.
        Проверяется, что пост не создан до отправки формы,
        форма заполняется корректно, данные сохраняются в БД и появляется
        запись в БД о новом посте.
        """
        form_data_create = {
            'text': 'Текст поста для проверки формы содания поста',
            'group': self.group.id,
            'image': self.image
        }
        posts_count_before_test = Post.objects.count()

        # Здесь мы проверяем, что изначально поста со значениеми из словаря
        # form_data_create не существует в БД перед отправкой запроса на
        # создание поста, добавили поле с картинкой
        self.assertFalse(
            Post.objects.filter(text=form_data_create['text'],
                                group=form_data_create['group'],
                                author=self.user,
                                image=self.image).exists()
        )
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data_create)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Здесь мы проверяем факт появления поста в БД, а так же, что поля
        # поста соответствуют переданным
        self.assertTrue(
            Post.objects.filter(text=form_data_create['text'],
                                group=form_data_create['group'],
                                author=self.user).exists()
        )
        # Проверяем, что создался только один пост
        posts_count_after_test = Post.objects.count()
        exp_num_posts_create = 1
        self.assertEqual(posts_count_after_test,
                         posts_count_before_test + exp_num_posts_create)

    def test_edit_post_valid_form(self):
        """
        Тестирование формы редактирования поста.
        Проверяется, что поля заполнены корректно,
        изменения сохраняются в БД и измененные данные соответствуют введенным.
        """
        form_data_edit = {
            'text': 'Текст поста для проверки формы редактирования поста',
            'group': self.another_group.id
        }
        self.assertNotEqual(self.post.text, form_data_edit['text'])
        self.assertEqual(self.post.group, self.group)

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data_edit
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data_edit['text'])
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.group.id, form_data_edit['group'])

        # проверяем, что пост не находится на странице старой группы
        response = self.authorized_client.get(reverse('posts:group_list',
                                                      args=[self.group.slug]))
        self.assertNotContains(response, self.post.text)

    def test_create_post_invalid_form(self):
        """Тестирование формы создания поста с некорректными данными."""
        form_data_create_invalid_text = {
            'text': '',
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create_invalid_text,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Post.objects.filter(
                text=form_data_create_invalid_text['text'], group=self.group
            ).exists()
        )
        # Проверяем поведение формы при условии, что пользователь неавторизован
        posts_count_before_test = Post.objects.count()
        form_data_create_invalid_client = {
            'text':
            'Текст поста для проверки формы неавторизованного пользователя',
            'group': self.group.id
        }
        response = self.client.post(
            reverse('posts:post_create'), data=form_data_create_invalid_client
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count_before_test)
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={reverse("posts:post_create")}'
        )

    def test_edit_post_invalid_form(self):
        """Тестирование формы редактирования поста с некорректными данными."""
        form_data_edit_invalid_text = {
            'text': '',
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data_edit_invalid_text,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.text,
                            form_data_edit_invalid_text['text'])

    def test_comment_form(self):
        """Тестирование формы комментариев"""
        # Проверям поведение, если пользователь не авторизован
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            {'text': 'Test comment'}
        )
        self.assertEqual(Comment.objects.count(), 0)

        # Проверям поведение, если пользователь авторизован
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            {'text': 'Test comment'}
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, 'Test comment')

        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertContains(response, 'Test comment')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_group(cls.group)
        const.delete_test_group(cls.another_group)
        const.delete_test_user(cls.user)
