from django.contrib import admin

from .models import Post, Group


# Определяем класс PostAdmin, который будет использоваться для отображения
# модели Post в админке
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


# Регистрируем модель Post в админке, используя класс PostAdmin для отображения
admin.site.register(Post, PostAdmin)
# Регистрируем модель Group в админке без дополнительных настроек отображения
admin.site.register(Group)
