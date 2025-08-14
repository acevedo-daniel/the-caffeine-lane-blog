from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Category, Comment, Post


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")
    comments = post.comments.filter(is_active=True, parent=None)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("login")

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()

            messages.success(request, "Comment added successfully!")
            return redirect("post_detail", slug=post.slug)
        else:
            messages.error(
                request,
                "There was an error with your comment. Please try again.",
            )
    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status="published").order_by(
        "-created_at"
    )
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "posts/category_view.html", context)


@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        messages.success(request, "Comment edited successfully.")
        return redirect("post_detail", slug=comment.post.slug)

    context = {"form": form, "comment": comment}
    return render(request, "posts/comment_edit.html", context)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, "You do not have permission to delete this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect("post_detail", slug=comment.post.slug)

    context = {"comment": comment}
    return render(request, "posts/comment_delete_confirm.html", context)
