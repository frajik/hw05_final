from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Group, User, Follow
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

set_limit: int = 10
title_limit: int = 30


@cache_page(20, key_prefix='index_page')
@vary_on_cookie
def index(request):
    template = "posts/index.html"
    posts = Post.objects.select_related("group")
    paginator = Paginator(posts, set_limit)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    context = {
        "page_obj": page_obj,
        "posts": posts,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("group")
    paginator = Paginator(posts, set_limit)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    context = {
        "page_obj": page_obj,
        "group": group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    count_posts = posts.count()
    paginator = Paginator(posts, set_limit)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        "author": author,
        "posts": posts,
        "count_posts": count_posts,
        "page_obj": page_obj,
        "following": following

    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    username = get_object_or_404(User, id=post.author_id)
    count_posts = Post.objects.filter(author=username).count()
    comments = post.comments.all()
    form = CommentForm()
    title = post.text[:title_limit]
    context = {
        "post": post,
        "username": username,
        "count_posts": count_posts,
        "title": title,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST" or None:
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", username=post.author.username)
        context = {
            "form": form,
        }
        return render(request, "posts/create_post.html", context)
    form = PostForm()
    context = {
        "form": form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    is_edit = True
    if post.author.username != request.user.username:
        return redirect("posts:post_detail", post_id=post.id)
    if form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post_id=post.id)
    context = {
        "form": form,
        "post": post,
        "is_edit": is_edit,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comments = form.save(commit=False)
        comments.author = request.user
        comments.post = post
        comments.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.filter(
        author__following__user=request.user
    )
    paginator = Paginator(post, set_limit)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    context = {"page_obj": page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", author)


@login_required
def profile_unfollow(request, username):
    follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    follower.delete()
    return redirect("posts:profile", username)
