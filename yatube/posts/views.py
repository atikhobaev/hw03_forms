from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden


from .models import Post, Group
from .forms import PostForm

POST_QUANTITY = 10


def index(request):
    """Главная страница с постами."""
    posts = Post.objects.select_related('author').all()
    paginator = Paginator(posts, POST_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница группы с постами."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POST_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страница с постами автора."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POST_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': author.posts.count(),
        'paginator': paginator,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница одного поста."""
    post = get_object_or_404(Post, pk=post_id)

    context = {
        'post': post,
        'author': post.author,
        'posts_count': post.author.posts.count(),
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создать новый пост."""
    form = PostForm(
        request.POST or None,
    )

    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
    }

    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    """Отредактировать пост."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
    )

    if not request.user == post.author:
        return redirect('posts:post_detail', post_id=post_id)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)

    
