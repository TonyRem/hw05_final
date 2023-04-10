from django.core.paginator import Paginator
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache


from . import constants as const
from ..models import Post
from ..views import POSTS_PER_PAGE


class TaskViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = const.create_test_user()
        cls.group = const.create_test_group()
        cls.image = const.create_test_image()
        cls.another_group = const.create_test_group('Еще одна группа',
                                                    'another_group_slug')
        cls.post = const.create_test_post(cls.author, cls.group)
        cls.another_post = const.create_test_post(
            cls.author, cls.group, cls.image)
        cls.post_list = Post.objects.all()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:home'):
            'posts/index.html',
            reverse('posts:group_list', args=[self.group.slug]):
            'posts/group_list.html',
            reverse('posts:profile', args=[self.author.username]):
            'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.id]):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', args=[self.post.id]):
            'posts/create_post.html',
            reverse('posts:search_results'):
            'posts/search_results.html',
        }
        for reverse_name, template_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template_name)

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:home'))
        page_objects = response.context['page_obj']
        paginator = Paginator(self.post_list, POSTS_PER_PAGE)
        first_object = response.context['page_obj'][0]

        post_values_types = {
            'text': forms.fields.CharField,
            'pub_date': forms.fields.DateTimeField,
            'group': forms.ModelChoiceField,
            'author': forms.ModelChoiceField,
            'image': forms.fields.ImageField
        }

        expected_page_context = {
            'title': 'Последние обновления на сайте',
            'header': 'Это главная страница сайта Yatube',
            'page_obj': page_objects,
        }

        self.assertEqual(len(page_objects), len(paginator.get_page(1)))

        for key, expected in post_values_types.items():
            with self.subTest(key=key):
                field = first_object._meta.get_field(key)
                self.assertIsInstance(field.formfield(), expected)
                self.assertEqual(getattr(first_object, key),
                                 getattr(self.another_post, key))

        for key, value in expected_page_context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], value)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                                      args=[self.group.slug]))
        page_objects = response.context['page_obj']
        paginator = Paginator(self.group.posts.all(), POSTS_PER_PAGE)

        expected_page_context = {
            'group': self.group,
            'page_obj': page_objects,
        }

        self.assertEqual(len(page_objects), len(paginator.get_page(1)))

        for post in page_objects:
            self.assertEqual(post.group, self.group)

        for key, value in expected_page_context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], value)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              args=[self.author.username]))
        page_objects = response.context['page_obj']
        paginator = Paginator(self.author.posts.all(), POSTS_PER_PAGE)

        expected_page_context = {
            'author': self.author,
            'page_obj': page_objects,
        }

        self.assertEqual(len(page_objects), len(paginator.get_page(1)))

        for post in page_objects:
            self.assertEqual(post.author, self.author)

        for key, value in expected_page_context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], value)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      args=[self.post.id]))

        self.assertEqual(response.context['post'], self.post)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        expected_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField
        }

        expected_page_context = {
            'form': response.context['form']
        }

        for value, expected in expected_form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        for key, value in expected_page_context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], value)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=[self.post.id]))

        expected_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField

        }

        expected_page_context = {
            'form': response.context['form'],
            'is_edit': True
        }

        for value, expected in expected_form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        for key, value in expected_page_context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], value)

    def test_post_does_not_belong_to_anoter_group(self):
        """Проверяем, что пост не попал в группу, для которой он не
        предназначен"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.another_group.slug])
        )
        self.assertNotContains(response, self.post.text)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_user(cls.author)
        const.delete_test_group(cls.group)
