from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count , Q
from django.contrib import messages
from django.utils.text import slugify
from landingpage.models import *
from .forms import *
from django.db import transaction

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

# @login_required
# def blog_list(request):
#     """Display a list of all blogs with search and filter options."""
#     blogs = BlogPost.objects.all().order_by('-created_at')
    
#     # Filter by search query
#     search_query = request.GET.get('search', '')
#     if search_query:
#         blogs = blogs.filter(
#             Q(title__icontains=search_query) | 
#             Q(content__icontains=search_query) |
#             Q(excerpt__icontains=search_query)
#         )
    
#     # Filter by status
#     status = request.GET.get('status', '')
#     if status == 'published':
#         blogs = blogs.filter(is_published=True)
#     elif status == 'draft':
#         blogs = blogs.filter(is_published=False)
    
#     # Pagination
#     paginator = Paginator(blogs, 10)  # Show 10 blogs per page
#     page = request.GET.get('page', 1)
#     blogs = paginator.get_page(page)
    
#     context = {
#         'active_page': 'blogs',
#         'blogs': blogs,
#     }
#     return render(request, 'admin/blogs/list.html', context)

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

# @login_required
# def blog_edit(request, blog_id):
#     """Edit an existing blog post."""
#     blog = get_object_or_404(Blog, id=blog_id)
    
#     if request.method == 'POST':
#         form = BlogForm(request.POST, request.FILES, instance=blog)
#         if form.is_valid():
#             blog = form.save(commit=False)
            
#             # Generate slug if not provided
#             if not BlogPost.slug:
#                 BlogPost.slug = slugify(BlogPost.title)
            
#             BlogPost.save()
            
#             # Handle tags (if your model uses a ManyToMany relationship)
#             if 'tags' in form.cleaned_data:
#                 BlogPost.tags.clear()
#                 if form.cleaned_data['tags']:
#                     tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
#                     for tag_name in tags:
#                         tag, created = Tag.objects.get_or_create(name=tag_name)
#                         BlogPost.tags.add(tag)
            
#             messages.success(request, 'Blog post updated successfully!')
#             return redirect('admin_blogs')
#     else:
#         # Prepare tags string for the form
#         tags = ', '.join([tag.name for tag in BlogPost.tags.all()]) if hasattr(blog, 'tags') else ''
        
#         # Initialize form with blog instance
#         form = BlogForm(instance=blog, initial={'tags': tags})
    
#     context = {
#         'active_page': 'blogs',
#         'blog': blog,
#         'form': form,
#         #'categories': Category.objects.all(),
#     }
#     return render(request, 'admin/blogs/form.html', context)

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
    plans = UserSubscription.objects.all()
    
    context = {
        'active_page': 'subscriptions',
        'plans': plans,
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

# @login_required
# def subscription_delete(request, plan_id):
#     """Delete a subscription plan."""
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
#     if request.method == 'POST':
#         plan.delete()
#         messages.success(request, 'Subscription plan deleted successfully!')
    
#     return redirect('admin_subscriptions')

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

# @login_required
# def faq_list(request):
#     """Display a list of all FAQs with search and filter options."""
#     faqs = FAQ.objects.all().order_by('category', 'order')
    
#     # Filter by search query
#     search_query = request.GET.get('search', '')
#     if search_query:
#         faqs = faqs.filter(
#             Q(question__icontains=search_query) | 
#             Q(answer__icontains=search_query)
#         )
    
#     # Filter by category
#     category_id = request.GET.get('category', '')
#     if category_id:
#         faqs = faqs.filter(category_id=category_id)
    
#     # Pagination
#     paginator = Paginator(faqs, 15)  # Show 15 FAQs per page
#     page = request.GET.get('page', 1)
#     faqs = paginator.get_page(page)
    
#     context = {
#         'active_page': 'faqs',
#         'faqs': faqs,
#         #'categories': Category.objects.all(),
#     }
#     return render(request, 'admin/faqs/list.html', context)

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