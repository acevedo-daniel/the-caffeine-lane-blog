from django.urls import path
from . import views

urlpatterns = [
    # Listado de posts
    path('', views.PostListView.as_view(), name='post_list'),
    path('category/<slug:category_slug>/', views.PostByCategoryView.as_view(), name='post_by_category'),
    
    # CRUD de posts
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Comentarios
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('<slug:slug>/comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # Vistas de usuario
    path('author/<str:username>/', views.AuthorPostsView.as_view(), name='author_posts'),
    path('my-posts/', views.UserPostsView.as_view(), name='user_posts'),
    
    # AJAX y utilidades
    path('ajax/search/', views.post_search_ajax, name='post_search_ajax'),
    path('ajax/comment/<int:comment_id>/toggle/', views.toggle_comment_status, name='toggle_comment_status'),
    
    # Feeds
    path('feed/', views.latest_posts_feed, name='posts_feed'),
]