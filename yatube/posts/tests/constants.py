"""
Модуль содержит вспомогательные функции для тестирования приложения Yatube.
"""

from django.contrib.auth import get_user_model
from django.db.models import Model
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile
import os


User = get_user_model()


def create_test_image() -> SimpleUploadedFile:
    image_name = 'test_image.jpg'
    test_image_path = os.path.join(os.path.dirname(__file__), image_name)
    with open(test_image_path, 'rb') as f:
        return SimpleUploadedFile(name=image_name,
                                  content=f.read(),
                                  content_type='image/jpeg')


def create_test_user(username: str = 'NoName') -> User:
    """Создает тестового пользователя."""
    return User.objects.create(username=username)


def create_test_group(title: str = 'Тестовая группа',
                      slug: str = 'Test-slug') -> Group:
    """Создает тестовую группу."""
    return Group.objects.create(
        title=title,
        slug=slug,
        description='Тестовое описание',
    )


def create_test_post(user: User, group: Group = None, image=None) -> Post:
    """Создает тестовый пост от заданного пользователя в указанной группе."""
    return Post.objects.create(
        author=user,
        text='Тестовый пост, больше 15 символов',
        group=group,
        image=image
    )


def delete_test_group(group: Model) -> None:
    """Удаляет тестовую группу."""
    group.delete()


def delete_test_user(user: Model) -> None:
    """Удаляет тестового пользователя."""
    user.delete()
