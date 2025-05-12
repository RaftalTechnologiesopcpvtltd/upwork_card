from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count , Q
from django.contrib import messages
from django.utils.text import slugify
from landingpage.models import *
from .forms import *
from django.db import transaction
import stripe

# Dashboard
@login_required
def dashboard(request):
    """Display the admin dashboard with summary statistics and recent items."""
    context = {
        'active_page': 'dashboard',
        'SearchHistory_count': SearchHistory.objects.count(),
        'SearchHistory': SearchHistory.objects.all().order_by('-created')[:3],
        'all_user' : CustomUser.objects.all(),
        'all_user_count' : CustomUser.objects.count(),
        'subscription_count': UserSubscription.objects.filter(active = True).count(),
        'subscriptions': UserSubscription.objects.filter(active = True).order_by('-start_date')[:3],
        'blog_count': BlogPost.objects.count(),
        'recent_blogs': BlogPost.objects.order_by('-created_at').annotate(comment_count=Count('comments'))[:3],
        'pricings' : Pricing.objects.all(),
        'faqs' : FAQ.objects.all(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def user_list(request):
    context = {
        'active_page': 'users',
        'all_user' : CustomUser.objects.all(),
    }
    return render(request, 'admin/user_list.html', context)

@login_required
def user_edit(request, user_id):
    """Edit an existing subscription plan."""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            return redirect('admin_users')  # Replace with your actual redirect URL name
    else:
        form = CustomUserForm(instance=user)
    
    context = {
        'active_page': 'users',
        'user': user,
        'form': form,
    }
    return render(request, 'admin/user_form.html', context)

@login_required
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('admin_users')  # Change to your actual list view name

@login_required
def search_history(request):
    context = {
        'search_history': SearchHistory.objects.all().order_by('-created'),
        'active_page': 'Search History',
    }
    return render(request, 'admin/search_history.html', context)

@login_required
def blog_list(request):
    """Display a list of all blogs with search and filter options."""
    blogs = BlogPost.objects.all().order_by('-created_at')

    blogs = blogs.annotate(comment_count=Count('comments'))
    
    # print(blogs[1].comments.all())
    
    
    context = {
        'active_page': 'blogs',
        'blogs': blogs,
    }
    return render(request, 'admin/blog_list.html', context)

@login_required
def blog_comment_list(request, post_id):
    """Display a list of all blogs with search and filter options."""
    post = get_object_or_404(BlogPost, id=post_id)    
    comments = Comment.objects.filter(post=post)
   
    context = {
        'active_page': 'blogs',
        'comments': comments,
    }
    return render(request, 'admin/comments_list.html', context)

@login_required
def approve_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.approved = not comment.approved  # toggle
        comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'blog_comment_list'))


# @login_required
# def blog_view(request, blog_id):
#     """Display a single blog post in detail."""
#     blog = get_object_or_404(BlogPost, id=blog_id)
    
#     context = {
#         'active_page': 'blogs',
#         'blog': blog,
#     }
#     return render(request, 'admin/blogs/view.html', context)

# @login_required
# def blog_add(request):
#     """Add a new blog post."""
#     if request.method == 'POST':
#         form = BlogForm(request.POST, request.FILES)
#         if form.is_valid():
#             blog = form.save(commit=False)
            
#             # Set the author to the current user
#             BlogPost.author = request.user
            
#             # Generate slug if not provided
#             if not BlogPost.slug:
#                 BlogPost.slug = slugify(BlogPost.title)
            
#             BlogPost.save()
            
#             # Handle tags (if your model uses a ManyToMany relationship)
#             if 'tags' in form.cleaned_data and form.cleaned_data['tags']:
#                 tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
#                 for tag_name in tags:
#                     tag, created = Tag.objects.get_or_create(name=tag_name)
#                     BlogPost.tags.add(tag)
            
#             messages.success(request, 'Blog post created successfully!')
#             return redirect('admin_blogs')
#     else:
#         form = BlogForm()
    
#     context = {
#         'active_page': 'blogs',
#         'form': form,
#         #'categories': Category.objects.all(),
#     }
#     return render(request, 'admin/blogs/form.html', context)

@login_required
def blog_edit(request, blog_id):
    """Edit an existing blog post."""
    blog = get_object_or_404(BlogPost, id=blog_id)

    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('admin_blogs')
        else:
            print("Form Errors:", form.errors)
    else:
        # Set tags as comma-separated string
        initial_tags = ', '.join(tag.name for tag in blog.tags.all())
        form = BlogPostForm(instance=blog, initial={'tags': initial_tags})
    
    context = {
        'active_page': 'blogs',
        'blog': blog,
        'form': form,
        #'categories': Category.objects.all(),
    }
    return render(request, 'admin/blog_form.html', context)

# @login_required
# def blog_delete(request, blog_id):
#     """Delete a blog post."""
#     blog = get_object_or_404(Blog, id=blog_id)
    
#     if request.method == 'POST':
#         BlogPost.delete()
#         messages.success(request, 'Blog post deleted successfully!')
    
#     return redirect('admin_blogs')

@login_required
def subscription_list(request):
    """Display a list of all subscription plans."""
    subscription = UserSubscription.objects.all().order_by("-start_date")
    subscription_history = SubscriptionHistory.objects.all().order_by("-start_date")

    for sub in subscription:
        for hist in subscription_history:
            if sub.subscription_id == hist.subscription_id:
                sub.was_renewed = hist.was_renewed
                sub.cancel_at = hist.cancel_at

    
    context = {
        'active_page': 'subscriptions',
        'plans': subscription.order_by("-id"),
    }
    return render(request, 'admin/subscription_list.html', context)

# @login_required
# def subscription_add(request):
#     """Add a new subscription plan."""
#     if request.method == 'POST':
#         form = SubscriptionPlanForm(request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 # Save the plan
#                 plan = form.save()
                
#                 # Process features
#                 features = request.POST.getlist('features[]')
#                 for feature_text in features:
#                     if feature_text.strip():
#                         PlanFeature.objects.create(
#                             plan=plan,
#                             description=feature_text.strip()
#                         )
                
#                 messages.success(request, 'Subscription plan created successfully!')
#                 return redirect('admin_subscriptions')
#     else:
#         form = SubscriptionPlanForm(initial={'is_active': True, 'duration_unit': 'months'})
    
#     context = {
#         'active_page': 'subscriptions',
#         'form': form,
#     }
#     return render(request, 'admin/subscriptions/form.html', context)

@login_required
def subscription_edit(request, plan_id):
    """Edit an existing subscription plan."""
    plan = get_object_or_404(UserSubscription, id=plan_id)
    
    if request.method == 'POST':
        form = UserSubscriptionForm(request.POST, instance=plan)
        
        if form.is_valid():
            form.save()
            return redirect('admin_subscriptions')  # Replace with your actual redirect URL name
    else:
        form = UserSubscriptionForm(instance=plan)
    
    context = {
        'active_page': 'subscriptions',
        'plan': plan,
        'form': form,
    }
    return render(request, 'admin/subscription_form.html', context)

@login_required
def subscription_cancel(request):
    try:
        subscription_id = request.POST.get("subscription_id")
        cancel_now = request.POST.get("cancel_now", False)  # Default: Cancel at end of period
        subscription = UserSubscription.objects.filter(subscription_id=subscription_id)

        print("subscription_id :",subscription_id)
        print("cancel_now: ",cancel_now)

        if cancel_now:
            stripe.Subscription.delete(subscription_id)  # Cancel Immediately
            subscription.delete()
            print(subscription)
            return redirect("admin_subscriptions")
        else:
            stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)  # Cancel at end
            return redirect("admin_subscriptions")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@login_required
def pricing_list(request):
    try:
        pricings = Pricing.objects.all()

        return render(request, 'admin/pricing_list.html', {"pricings":pricings})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400) 

# @login_required
# def slider_list(request):
#     """Display a list of all sliders."""
#     sliders = Slidder.objects.all().order_by('order')
    
#     context = {
#         'active_page': 'sliders',
#         'sliders': sliders,
#     }
#     return render(request, 'admin/sliders/list.html', context)

# @login_required
# def slider_add(request):
#     """Add a new Slidder."""
#     if request.method == 'POST':
#         form = SliderForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Slider created successfully!')
#             return redirect('admin_sliders')
#     else:
#         # Get the highest order value and add 1
#         try:
#             last_order = Slidder.objects.order_by('-order').first().order
#             next_order = last_order + 1
#         except (AttributeError, Slidder.DoesNotExist):
#             next_order = 1
            
#         form = SliderForm(initial={'is_active': True, 'order': next_order})
    
#     context = {
#         'active_page': 'sliders',
#         'form': form,
#     }
#     return render(request, 'admin/sliders/form.html', context)

# @login_required
# def slider_edit(request, slider_id):
#     """Edit an existing Slidder."""
#     slider = get_object_or_404(Slidder, id=slider_id)
    
#     if request.method == 'POST':
#         form = SliderForm(request.POST, request.FILES, instance=slider)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Slider updated successfully!')
#             return redirect('admin_sliders')
#     else:
#         form = SliderForm(instance=slider)
    
#     context = {
#         'active_page': 'sliders',
#         'slider': slider,
#         'form': form,
#     }
#     return render(request, 'admin/sliders/form.html', context)

# @login_required
# def slider_delete(request, slider_id):
#     """Delete a Slidder."""
#     slider = get_object_or_404(Slidder, id=slider_id)
    
#     if request.method == 'POST':
#         Slidder.delete()
#         messages.success(request, 'Slider deleted successfully!')
    
#     return redirect('admin_sliders')

@login_required
def faq_list(request):
    """Display a list of all FAQs with search and filter options."""
    faqs = FAQ.objects.all()
    
    
    
    context = {
        'active_page': 'faqs',
        'faqs': faqs,
        #'categories': Category.objects.all(),
    }
    return render(request, 'admin/faq_list.html', context)

# @login_required
# def faq_add(request):
#     """Add a new FAQ."""
#     if request.method == 'POST':
#         form = FAQForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'FAQ created successfully!')
#             return redirect('admin_faqs')
#     else:
#         # Get the highest order value and add 1
#         try:
#             last_order = FAQ.objects.order_by('-order').first().order
#             next_order = last_order + 1
#         except (AttributeError, FAQ.DoesNotExist):
#             next_order = 1
            
#         form = FAQForm(initial={'is_active': True, 'order': next_order})
    
#     context = {
#         'active_page': 'faqs',
#         'form': form,
#         #'categories': Category.objects.all(),
#     }
#     return render(request, 'admin/faqs/form.html', context)

# @login_required
# def faq_edit(request, faq_id):
#     """Edit an existing FAQ."""
#     faq = get_object_or_404(FAQ, id=faq_id)
    
#     if request.method == 'POST':
#         form = FAQForm(request.POST, instance=faq)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'FAQ updated successfully!')
#             return redirect('admin_faqs')
#     else:
#         form = FAQForm(instance=faq)
    
#     context = {
#         'active_page': 'faqs',
#         'faq': faq,
#         'form': form,
#         #'categories': Category.objects.all(),
#     }
#     return render(request, 'admin/faqs/form.html', context)

# @login_required
# def faq_delete(request, faq_id):
#     """Delete a FAQ."""
#     faq = get_object_or_404(FAQ, id=faq_id)
    
#     if request.method == 'POST':
#         faq.delete()
#         messages.success(request, 'FAQ deleted successfully!')
    
#     return redirect('admin_faqs')

# @login_required
# def contact_list(request):
#     """Display a list of all contact messages with search and filter options."""
#     contacts = ContactMessage.objects.all().order_by('-created_at')
    
#     # Filter by search query
#     search_query = request.GET.get('search', '')
#     if search_query:
#         contacts = contacts.filter(
#             Q(name__icontains=search_query) | 
#             Q(email__icontains=search_query) |
#             Q(subject__icontains=search_query) |
#             Q(message__icontains=search_query)
#         )
    
#     # Filter by status
#     status = request.GET.get('status', '')
#     if status == 'read':
#         contacts = contacts.filter(is_read=True)
#     elif status == 'unread':
#         contacts = contacts.filter(is_read=False)
    
#     # Pagination
#     paginator = Paginator(contacts, 15)  # Show 15 contacts per page
#     page = request.GET.get('page', 1)
#     contacts = paginator.get_page(page)
    
#     context = {
#         'active_page': 'contacts',
#         'contacts': contacts,
#     }
#     return render(request, 'admin/contacts/list.html', context)

# @login_required
# def contact_mark_read(request, contact_id):
#     """Mark a contact message as read."""
#     contact = get_object_or_404(ContactMessage, id=contact_id)
    
#     if request.method == 'POST':
#         ContactMessage.is_read = True
#         ContactMessage.save()
#         messages.success(request, 'Message marked as read.')
    
#     return redirect('admin_contacts')

# @login_required
# def contact_delete(request, contact_id):
#     """Delete a contact message."""
#     contact = get_object_or_404(ContactMessage, id=contact_id)
    
#     if request.method == 'POST':
#         ContactMessage.delete()
#         messages.success(request, 'Message deleted successfully!')
    
#     return redirect('admin_contacts')