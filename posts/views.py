from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def page_paginator(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def index(request):
    post_list = Post.objects.all()
    return render(request,
                  'index.html',
                  {'page': page_paginator(request, post_list)}
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    return render(request,
                  'group.html',
                  {'group': group,
                   'page': page_paginator(request, post_list)}
                  )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    edit = author == request.user
    post_list = author.posts.all()
    post_count = post_list.count()
    context = {'post_count': post_count,
               'author': author,
               'page': page_paginator(request, post_list),
               'edit': edit}
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    edit = author == request.user
    post_count = author.posts.count()
    post = get_object_or_404(Post, author__username=username, id=post_id)

    context = {'post_count': post_count,
               'post': post,
               'author': author,
               'edit': edit}
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('posts:post',
                        post_id=post.id,
                        username=post.author.username)

    form = PostForm(request.POST or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post',
                            username=request.user.username,
                            post_id=post_id)

    return render(request, 'new.html', {'form': form, 'edit': True})
