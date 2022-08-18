from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Group, User
from .forms import PostForm

POSTS_AMOUNT = 10


def index(request):
    posts = Post.objects.all()
    page_obj = paginate_posts(request, posts)
    template = 'posts/index.html'

    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate_posts(request, posts)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_amount = author.posts.count()

    page_obj = paginate_posts(request, posts)

    context = {
        'page_obj': page_obj,
        'author': author,
        'posts_amount': posts_amount,
    }
    return render(request, template, context)


def paginate_posts(request, posts):
    paginator = Paginator(posts, POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def post_detail(request, post_id):
    template = 'posts/post_detail.html'

    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:30]
    post_pub_date = post.pub_date
    author = post.author
    author_posts_amount = author.posts.all().count()

    context = {
        "post": post,
        "post_title": post_title,
        "pub_date": post_pub_date,
        "author": author,
        "author_posts_amount": author_posts_amount,
    }

    return render(request, template, context)


@login_required
def post_create(request):

    template = "posts/create_post.html"
    form = PostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", post.author)

    context = {
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):

    template = "posts/create_post.html"

    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    form = PostForm(request.POST or None, instance=post)

    if request.user == author:
        if request.method == "POST" and form.is_valid:
            post = form.save()
            return redirect("posts:post_detail", post_id)

        context = {
            "is_edit": is_edit,
            "form": form,
        }

        return render(request, template, context)
    return redirect("posts:post_detail", post_id)
