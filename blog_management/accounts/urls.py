from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from . import views
from .views import update_profile

urlpatterns = [
    # User Authentication URLs
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('admin/auth/user/', lambda request: redirect('/admin/accounts/customuser/')),  # Redirect for admin user management
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', update_profile, name='update_profile'),

    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Home Page URL
    path('', views.home, name='home'),

    # Blog URLs
    path('create_blog/', views.create_blog, name='create_blog'),
    path('edit_blog/<int:id>/', views.blog_edit, name='blog_edit'),
    path('blog_delete/<int:id>/', views.blog_delete, name='blog_delete'),
    path('blog_list/', views.blog_list, name='blog_list'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    
    # Commenting functionality for blog posts
    path('add_comment/<int:blog_id>/', views.add_comment, name='add_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
