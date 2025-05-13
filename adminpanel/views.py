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
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test



@user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    context = {
        'active_page': 'users',
        'all_user' : CustomUser.objects.all(),
    }
    return render(request, 'admin/user_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    """Edit an existing subscription plan."""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user, editing=True)
        
        if form.is_valid():
            form.save()
            return redirect('admin_users')  # Replace with your actual redirect URL name
    else:
        form = CustomUserForm(instance=user, editing=True)
    
    context = {
        'active_page': 'users',
        'user': user,
        'form': form,
    }
    return render(request, 'admin/user_form.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_add(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data['username'] = data['email']
        form = CustomUserForm(data, editing=False)  # Not editing
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('admin_users')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = CustomUserForm(editing=False)
    context = {
        'active_page': 'users',
        'form': form,
    }
    return render(request, 'admin/user_form.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('admin_users')  # Change to your actual list view name

@user_passes_test(lambda u: u.is_superuser)
def search_history(request):
    context = {
        'search_history': SearchHistory.objects.all().order_by('-created'),
        'active_page': 'Search History',
    }
    return render(request, 'admin/search_history.html', context)

@user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
def blog_comment_list(request, post_id):
    """Display a list of all blogs with search and filter options."""
    post = get_object_or_404(BlogPost, id=post_id)    
    comments = Comment.objects.filter(post=post)
   
    context = {
        'active_page': 'blogs',
        'comments': comments,
    }
    return render(request, 'admin/comments_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def approve_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.approved = not comment.approved  # toggle
        comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'blog_comment_list'))


@user_passes_test(lambda u: u.is_superuser)
def blog_view(request, blog_id):
    """Display a single blog post in detail."""
    blog = BlogPost.objects.annotate(
    comment_count=Count('comments')
).prefetch_related('comments__user').get(id=blog_id)
    
    context = {
        'active_page': 'blogs',
        'blog': blog,
    }
    return render(request, 'admin/blog_view.html', context)

@user_passes_test(lambda u: u.is_superuser)
def blog_add(request):
    """Add a new blog post."""
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save tags
            return redirect('admin_blogs')
    else:
        form = BlogPostForm()
    
    context = {
        'active_page': 'blogs',
        'form': form,
    }
    return render(request, 'admin/blog_form.html', context)

@user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
def blog_delete(request, blog_id):
    """Delete a blog post."""
    blog = get_object_or_404(BlogPost, id=blog_id)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog post deleted successfully!')
    
    return redirect('admin_blogs')

@user_passes_test(lambda u: u.is_superuser)
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

# @user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
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
    
@user_passes_test(lambda u: u.is_superuser)
def pricing_list(request):
    try:
        pricings = Pricing.objects.all()

        return render(request, 'admin/pricing_list.html', {'active_page': 'Pricing',"pricings":pricings})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400) 
    

@user_passes_test(lambda u: u.is_superuser)
def pricing_add(request):
    if request.method == 'POST':
        form = PricingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pricing')  # Replace with your view name
    else:
        form = PricingForm()

    return render(request, 'admin/pricing_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def pricing_edit(request, pricing_id):
    """Edit an existing pricing."""
    pricing = get_object_or_404(Pricing, id=pricing_id)

    if request.method == 'POST':
        form = PricingForm(request.POST, instance=pricing)
        if form.is_valid():
            form.save()
            messages.success(request, 'pricing updated successfully!')
            return redirect('pricing')
    else:
        form = PricingForm(instance=pricing)

    context = {
        'active_page': 'Pricing',
        'pricing': pricing,
        'form': form,
    }
    return render(request, 'admin/pricing_form.html', context)
    
@user_passes_test(lambda u: u.is_superuser)
def pricing_delete(request, pricing_id):
    """Delete a blog post."""
    pricing = get_object_or_404(Pricing, id=pricing_id)
    
    if request.method == 'POST':
        pricing.delete()
        messages.success(request, 'Pricing deleted successfully!')
    
    return redirect('pricing')

@user_passes_test(lambda u: u.is_superuser)
def slider_list(request):
    """Display a list of all sliders."""
    sliders = Slidder.objects.all()
    
    context = {
        'active_page': 'sliders',
        'sliders': sliders,
    }
    return render(request, 'admin/slider_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def slider_add(request):
    """Add a new Slidder with correct ordering."""
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            new_slider = form.save(commit=False)
            desired_order = new_slider.order or 1

            # Shift existing sliders if needed
            Slidder.objects.filter(order__gte=desired_order).update(order=models.F('order') + 1)

            new_slider.order = desired_order
            new_slider.save()

            messages.success(request, 'Slider created successfully!')
            return redirect('admin_sliders')
    else:
        try:
            last_order = Slidder.objects.order_by('-order').first().order
            next_order = last_order + 1
        except (AttributeError, Slidder.DoesNotExist):
            next_order = 1

        form = SliderForm(initial={'is_active': True, 'order': next_order})

    context = {
        'active_page': 'sliders',
        'form': form,
    }
    return render(request, 'admin/slider_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def slider_edit(request, slider_id):
    """Edit an existing Slidder."""
    slider = get_object_or_404(Slidder, id=slider_id)

    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            Slidder.reorder_all()  # Auto reorder after any update
            messages.success(request, 'Slider updated successfully!')
            return redirect('admin_sliders')
    else:
        form = SliderForm(instance=slider)

    context = {
        'active_page': 'sliders',
        'slider': slider,
        'form': form,
    }
    return render(request, 'admin/slider_form.html', context)

@user_passes_test(lambda u: u.is_superuser)
def slider_delete(request, slider_id):
    """Delete a Slidder and reorder remaining ones."""
    slider = get_object_or_404(Slidder, id=slider_id)

    if request.method == 'POST':
        slider.delete()

        # Reorder remaining sliders
        Slidder.reorder_all()

        messages.success(request, 'Slider deleted successfully!')

    return redirect('admin_sliders')

@user_passes_test(lambda u: u.is_superuser)
def faq_list(request):
    """Display a list of all FAQs with search and filter options."""
    faqs = FAQ.objects.all()
    
    
    
    context = {
        'active_page': 'faqs',
        'faqs': faqs,
        #'categories': Category.objects.all(),
    }
    return render(request, 'admin/faq_list.html', context)


from django.db.models import F
@user_passes_test(lambda u: u.is_superuser)
def faq_add(request):
    """Add a new FAQ with proper ordering."""
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save(commit=False)
            desired_order = faq.order or 1

            # Shift existing FAQs
            FAQ.objects.filter(order__gte=desired_order).update(order=F('order') + 1)

            faq.order = desired_order
            faq.save()
            messages.success(request, 'FAQ added successfully!')
            return redirect('admin_faqs')  # or your URL name
    else:
        try:
            last_order = FAQ.objects.latest('order').order
            next_order = last_order + 1
        except FAQ.DoesNotExist:
            next_order = 1

        form = FAQForm(initial={'order': next_order, 'is_active': True})

    return render(request, 'admin/faq_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def faq_edit(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    old_order = faq.order

    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            updated_faq = form.save(commit=False)
            new_order = updated_faq.order

            if new_order != old_order:
                if new_order < old_order:
                    FAQ.objects.filter(order__gte=new_order, order__lt=old_order).exclude(id=faq.id).update(order=F('order') + 1)
                else:
                    FAQ.objects.filter(order__gt=old_order, order__lte=new_order).exclude(id=faq.id).update(order=F('order') - 1)

            updated_faq.save()
            messages.success(request, 'FAQ updated successfully!')
            return redirect('admin_faqs')
    else:
        form = FAQForm(instance=faq)

    return render(request, 'admin/faq_form.html', {'form': form,'faq':faq})


@user_passes_test(lambda u: u.is_superuser)
def faq_delete(request, faq_id):
    """Delete a FAQ."""
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ deleted successfully!')
    
    return redirect('admin_faqs')

@user_passes_test(lambda u: u.is_superuser)
def contact_list(request):
    """Display a list of all contact messages with search and filter options."""
    contacts = ContactMessage.objects.all().order_by('-created_at')
    
    
    context = {
        'active_page': 'contacts',
        'contacts': contacts,
    }
    return render(request, 'admin/contact_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def contact_mark_read(request, contact_id):
    """Mark a contact message as read."""
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if request.method == 'POST':
        contact.status = True
        contact.save()
        messages.success(request, 'Message marked as read.')
    
    return redirect('admin_contacts')

@user_passes_test(lambda u: u.is_superuser)
def contact_delete(request, contact_id):
    """Delete a contact message."""
    contact = get_object_or_404(ContactMessage, id=contact_id)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Message deleted successfully!')
    
    return redirect('admin_contacts')

# Create
@user_passes_test(lambda u: u.is_superuser)
def contactus_create(request):
    if request.method == 'POST':
        form = ContactusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contactus_list')
    else:
        form = ContactusForm()
    return render(request, 'admin/contactus_form.html', {'form': form})

# Read (List)
@user_passes_test(lambda u: u.is_superuser)
def contactus_list(request):
    contactus_entries = Contactus.objects.all()
    return render(request, 'admin/contactus_list.html', {'contactus_entries': contactus_entries})

# Update
@user_passes_test(lambda u: u.is_superuser)
def contactus_update(request, pk):
    contact = get_object_or_404(Contactus, pk=pk)
    if request.method == 'POST':
        form = ContactusForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contactus_list')
    else:
        form = ContactusForm(instance=contact)
    return render(request, 'admin/contactus_form.html', {'form': form})

# Delete
@user_passes_test(lambda u: u.is_superuser)
def contactus_delete(request, pk):
    contact = get_object_or_404(Contactus, pk=pk)
    if request.method == 'POST':
        contact.delete()
        return redirect('contactus_list')