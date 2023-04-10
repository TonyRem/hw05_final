from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from django.core.cache import cache


from . import constants as const


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = const.create_test_user()
        cls.author = const.create_test_user(username='author')
        cls.group = const.create_test_group()
        cls.post = const.create_test_post(cls.author)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author.force_login(self.author)
        cache.clear()

    def test_urls_guest_user(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        non_existent_page_url = '/posts/non-existent-page/'
        urls = {
            reverse('posts:home'): HTTPStatus.OK,
            reverse('posts:group_list', args=[self.group.slug]): HTTPStatus.OK,
            reverse('posts:profile', args=[self.user.username]): HTTPStatus.OK,
            reverse('posts:post_detail', args=[self.post.id]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse('posts:post_edit', args=[self.post.id]): HTTPStatus.FOUND,
            reverse('posts:search_results'): HTTPStatus.OK,
            non_existent_page_url: HTTPStatus.NOT_FOUND,


        }
        for url, expected_status_code in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if expected_status_code == HTTPStatus.FOUND:
                    self.assertRedirects(
                        response, f"{reverse('users:login')}?next={url}"
                    )
                self.assertEqual(response.status_code, expected_status_code)

    def test_urls_authorized_user(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        non_existent_page_url = '/ posts/non-existent-page/'
        urls = {
            reverse('posts:home'): HTTPStatus.OK,
            reverse('posts:group_list', args=[self.group.slug]): HTTPStatus.OK,
            reverse('posts:profile', args=[self.user.username]): HTTPStatus.OK,
            reverse('posts:post_detail', args=[self.post.id]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:search_results'): HTTPStatus.OK,
            non_existent_page_url: HTTPStatus.NOT_FOUND,
        }

        for url, expected_status_code in urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_status_code)

    def test_urls_post_edit(self):
        """Проверка доступности редактирования поста для автора и
        недоступности для стороннего пользователя."""
        url = reverse('posts:post_edit', args=[self.post.id])
        response = self.authorized_client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('posts:post_detail', args=[self.post.id])}"
        )

        response = self.authorized_client_author.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/search/': 'posts/search_results.html',
            '/ posts/non-existent-page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        const.delete_test_group(cls.group)
        const.delete_test_user(cls.user)
        const.delete_test_user(cls.author)
