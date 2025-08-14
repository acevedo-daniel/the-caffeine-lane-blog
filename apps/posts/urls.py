
from django.urls import path

from . import views

urlpatterns = [
    path("category/<slug:category_slug>/", views.category_view, name="category_view"),
    path("comments/<int:comment_id>/edit/", views.comment_edit, name="comment_edit"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]