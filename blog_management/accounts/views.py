from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserUpdateForm, BlogForm, CommentForm  # Added CommentForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator as token_generator
from .models import CustomUser, Blog, Comment  # Import Blog and Comment models
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def send_account_blocked_email(user):
    subject = 'Your account has been blocked'
    message = render_to_string('account_blocked_email.html', {'user': user})

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

# Example usage
def block_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_active = False
    user.save()

    send_account_blocked_email(user)  # Send the email

    return redirect('admin_dashboard')

def block_post(request, post_id):
    blog = Blog.objects.get(id=post_id)
    blog.is_active = False  # Mark the post as inactive (blocked)
    blog.save()

    # Send email notification to the blog author
    send_mail(
        'Your blog post has been blocked',
        'Dear {},\n\nYour blog post "{}" has been blocked by the admin. Please review the content and contact support if you believe this is an error.\n\nBest regards,\nThe Team'.format(blog.author.username, blog.title),
        settings.DEFAULT_FROM_EMAIL,
        [blog.author.email],
        fail_silently=False,
    )

    return redirect('admin_dashboard')  # Redirect to the admin dashboard or appropriate page

def delete_post(request, post_id):
    blog = Blog.objects.get(id=post_id)
    blog.delete()

    # Send email notification to the blog author
    send_mail(
        'Your blog post has been deleted',
        'Dear {},\n\nYour blog post "{}" has been permanently deleted by the admin. If you believe this is an error, please contact support.\n\nBest regards,\nThe Team'.format(blog.author.username, blog.title),
        settings.DEFAULT_FROM_EMAIL,
        [blog.author.email],
        fail_silently=False,
    )

    return redirect('admin_dashboard')  

def block_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_active = False  # Mark user as inactive (blocked)
    user.save()

    # Send email notification
    send_mail(
        'Your account has been blocked',
        'Dear {},\n\nYour account has been blocked by the admin due to violation of our policies. If you think this is a mistake, please contact support.\n\nBest regards,\nThe Team'.format(user.username),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return redirect('admin_dashboard')  # Redirect to the admin dashboard or appropriate page

def delete_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()

    # Send email notification
    send_mail(
        'Your account has been deleted',
        'Dear {},\n\nYour account has been permanently deleted by the admin. If you believe this is an error, please contact support.\n\nBest regards,\nThe Team'.format(user.username),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return redirect('admin_dashboard') 

# Create Blog View
@login_required  # Ensure the user is logged in to create a blog
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user  # Set the current user as the blog author
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_list')  # Redirect to the blog list page after saving the blog
    else:
        form = BlogForm()

    return render(request, 'accounts/create_blog.html', {'form': form})


# Blog List View
def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'accounts/blog_list.html', {'blogs': blogs})


# Blog Detail View with Comments
def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    comments = blog.comments.all()  # Get all comments related to this blog

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog  # Set the blog to the current post
            new_comment.user = request.user  # Set the user to the current logged-in user
            new_comment.save()
            return redirect('blog_detail', id=blog.id)  # Redirect back to the same blog page
    else:
        comment_form = CommentForm()

    return render(request, 'accounts/blog_detail.html', {'blog': blog, 'comments': comments, 'comment_form': comment_form})


@login_required
def blog_edit(request, id):
    blog = get_object_or_404(Blog, id=id)

    if blog.author != request.user:
        messages.error(request, "You are not authorized to edit this blog post.")
        return redirect('home')

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect('blog_detail', id=blog.id)  # Redirect to blog detail page
    else:
        form = BlogForm(instance=blog)

    return render(request, 'accounts/blog_edit.html', {'form': form, 'blog': blog})


@login_required
def blog_delete(request, id):
    # Get the blog post with the given id
    blog = get_object_or_404(Blog, id=id)
    
    # Check if the user is the author of the blog post
    if blog.author == request.user:
        blog.delete()
        return redirect('home')  # Redirect to the home page or a success page
    else:
        # If the user is not the author, return an error or redirect
        return redirect('error_page')  # Replace with your error page or message


# Commenting functionality for blog posts
def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)  # Get the blog post

    if request.method == 'POST':
        form = CommentForm(request.POST)  # Create a form instance with the submitted data
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog  # Associate the comment with the current blog post
            comment.user = request.user  # Set the user who posted the comment
            comment.save()  # Save the comment to the database
            return redirect('blog_detail', pk=blog.id)  # Redirect back to the blog detail page

    else:
        form = CommentForm()  # Initialize an empty form if it's a GET request

    return render(request, 'accounts/add_comment.html', {'form': form, 'blog': blog})


# Forgot Password view (Step 1: User provides email)
def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            associated_users = CustomUser.objects.filter(email=email)  # Use CustomUser here
            if associated_users.exists():
                for user in associated_users:
                    # Generate password reset link
                    token = token_generator.make_token(user)
                    uid = urlsafe_base64_encode(str(user.pk).encode())
                    reset_url = reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    reset_link = get_current_site(request).domain + reset_url

                    # Send reset password email
                    subject = "Password Reset Request"
                    message = render_to_string('accounts/password_reset_email.html', {
                        'user': user,
                        'reset_link': reset_link,
                    })
                    send_mail(subject, message, 'your-email@example.com', [user.email])

                return HttpResponse("Password reset link has been sent to your email.")
            else:
                messages.error(request, "No user found with that email address.")
                return redirect('forgot_password')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


# Password Reset Confirmation View (Step 2: User clicks link to reset)
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('login')


# Update Profile View
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('update_profile')  # Redirect to the same page to clear the POST request
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})


# Register View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


# Home View
@login_required
def home(request):
    blogs = Blog.objects.all()  # Get all blogs to display in the home page
    return render(request, 'accounts/home.html', {'blogs': blogs})
