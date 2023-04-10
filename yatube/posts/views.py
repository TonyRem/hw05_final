from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.views.decorators.cache import cache_page

from .models import Post, Group, Comment, Follow, User
from .forms import PostForm, CommentForm


POSTS_PER_PAGE = 10
CACH_TIME = 20


@cache_page(CACH_TIME, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Последние обновления на сайте',
        'header': 'Это главная страница сайта Yatube',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method != 'POST' or not form.is_valid():
        return render(
            request, 'posts/create_post.html', context={'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


class SearchResultsView(ListView):
    model = Post
    template_name = 'posts/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        object_list = Post.objects.filter(text__icontains=query)
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    following = Follow.objects.filter(
        user=user).select_related('author').values('author')
    post_list = Post.objects.filter(author__in=following)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Ваши подписки',
        'header': 'Посты от авторов, на которых Вы подписаны',
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(
            user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
