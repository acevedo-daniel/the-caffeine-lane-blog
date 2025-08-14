from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from apps.posts.models import Category, Post

from .forms import ContactForm


def landing(request):
    return render(request, "core/landing.html")


def home(request):
    banner_posts = Post.objects.filter(status="published").order_by("-created_at")[:5]

    new_builds = Post.objects.filter(
        status="published", category__slug="builds"
    ).order_by("-created_at")[:9]

    new_guides = Post.objects.filter(
        status="published", category__slug="guides"
    ).order_by("-created_at")[:6]

    new_reviews = Post.objects.filter(
        status="published", category__slug="reviews"
    ).order_by("-created_at")[:4]
    total_posts = Post.objects.filter(status="published").count()
    categories = Category.objects.all()

    context = {
        "banner_posts": banner_posts,
        "new_builds": new_builds,
        "new_guides": new_guides,
        "new_reviews": new_reviews,
        "total_posts": total_posts,
        "categories": categories,
    }

    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["from_name"]
            email = form.cleaned_data["from_email"]
            subject = form.cleaned_data["subject"]
            message_text = form.cleaned_data["message"]

            full_message = f"From: {name} <{email}>\n\n{message_text}"

            send_mail(
                subject=f"Contact from Blog: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            messages.success(
                request, "Thank you for your message! We will get back to you soon."
            )
            return redirect("contact")
    else:
        form = ContactForm()
    context = {
        "form": form,
    }
    return render(request, "core/contact.html", context)
