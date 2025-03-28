from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import razorpay
import logging
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count , Q


def Landing_page(request):

    
    slidders = Slidder.objects.all()
    Contact = Contactus.objects.all()
    Pricings = Pricing.objects.all()

    User_Subscription = None
    

    if request.user.is_authenticated:
        try:
            # Check if the user has an active subscription
            subscription = UserSubscription.objects.get(user=request.user)
            if subscription.active:
                return redirect('dashboard_view')  # Redirect to dashboard if active subscription            
        except UserSubscription.DoesNotExist:
            context = {
                "User_Subscription" : User_Subscription,
                "slidders" : slidders,
                "Contact" : Contact,
                "Pricings" :Pricings
            }
            # If no subscription exists, show the landing page
            return render(request, 'home.html',context)
    
    context = {
        "User_Subscription" : User_Subscription,
        "slidders" : slidders,
        "Contact" : Contact,
        "Pricings" :Pricings
    }

    return render(request, 'home.html',context)


import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = request.POST.get('remember_me')
            login(request, user)
            
            # Log the successful login
            logger.debug(f'User {user.username} logged in.')
            
            # Print the session key for debugging purposes
            session_key = request.session.session_key
            print(f"Session key at login: {session_key}")  # Debug statement
            
            # Set session expiry based on "Remember Me" checkbox
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser session
            return redirect('landingpage')
        else:
            # Handle form errors
            print(form.errors)
            logger.error('Login failed: invalid form data')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})



# Initialize logger
logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount, session_key):
    """
    Create a Razorpay order.
    """
    try:
        data = {
            'amount': amount * 100,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '0',
            'receipt': session_key,
        }
        response_data = client.order.create(data)
        if response_data['status'] == 'created':
            logger.info(f"Razorpay order created: {response_data['id']} with session_key: {session_key}")
            return response_data['id']
        else:
            logger.error(f"Failed to create Razorpay order with session_key: {session_key}")
            return None
    except Exception as e:
        logger.error(f"Error while creating Razorpay order: {e}")
        return None



# Initialize logger
logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount, session_key):
    """
    Create a Razorpay order.
    """
    razorpay_amount = int(amount * 100)
    try:
        data = {
            'amount': razorpay_amount,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '0',
            'receipt': session_key,
        }
        response_data = client.order.create(data)
        if response_data['status'] == 'created':
            logger.info(f"Razorpay order created: {response_data['id']} with session_key: {session_key}")
            return response_data['id']
        else:
            logger.error(f"Failed to create Razorpay order with session_key: {session_key}")
            return None
    except Exception as e:
        logger.error(f"Error while creating Razorpay order: {e}")
        return None


@csrf_exempt
def paymenthandler(request):
    """
    Handle the Razorpay payment callback.
    """
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            if not (payment_id and razorpay_order_id and signature):
                logger.error(f"Missing parameters: payment_id={payment_id}, razorpay_order_id={razorpay_order_id}, signature={signature}")
                return HttpResponseBadRequest("Missing parameters.")

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            client.utility.verify_payment_signature(params_dict)

            # Fetch payment details and capture the payment
            payment_details = client.payment.fetch(payment_id)
            amount = payment_details['amount']

            client.payment.capture(payment_id, amount)

            # Update the subscription status
            subscription = UserSubscription.objects.get(receipt=razorpay_order_id)
            subscription.active = True
            subscription.payment_id = payment_id
            subscription.payment_status = 'captured'
            subscription.start_date = date.today()
            subscription.end_date = date.today() + timedelta(days=subscription.plan.duration_in_days)
            subscription.save()

            logger.info(f"Payment captured successfully for subscription {subscription.id}")
            # return redirect("dashboard_view")
            return render(request, 'subscription_success.html', {'plan': subscription.plan})

        except Exception as e:
            logger.error(f"Payment handler error: {e}")
            return render(request, 'paymentfail.html')
    else:
        return HttpResponseBadRequest()


@login_required
def subscribe_to_plan(request, plan_id):
    """
    Subscribe to a pricing plan.
    """
    plan = get_object_or_404(Pricing, id=plan_id)

    # Check if the user already has an active subscription
    try:
        active_subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        active_subscription = None

    # Create Razorpay order
    session_key = request.session.session_key or request.session.create()
    razorpay_order_id = create_razorpay_order(plan.price, session_key)
    if not razorpay_order_id:
        return HttpResponseBadRequest("Failed to create Razorpay order.")

    if active_subscription:
        if not active_subscription.active:
            # Deactivate the existing subscription and update with new receipt
            active_subscription.receipt = razorpay_order_id
            active_subscription.plan = plan
            active_subscription.save()
        else:
            # If there's already an active subscription, handle it accordingly
            return HttpResponseBadRequest("You already have an active subscription.")
    else:
        # Create a new subscription (inactive until payment is confirmed)
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            receipt=razorpay_order_id,
            active=False
        )

    context = {
        'user': request.user,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': plan.price,  # Amount in paise
        'plan': plan,
    }

    return render(request, 'payment_checkout.html', context)

@login_required
def dashboard_view(request):
    """
    Dashboard view for users with an active subscription.
    """
    slidders = Slidder.objects.all()

    try:
        subscription = UserSubscription.objects.get(user=request.user)
        if subscription.active:
            # Render the dashboard page if the subscription is active
            return render(request, 'dashboard.html',{"slidders" : slidders,"User_Subscription" : subscription,})  # Replace with your dashboard template
        else:
            # Redirect to landing page if the subscription is not active
            return redirect('landingpage')
    except UserSubscription.DoesNotExist:
        # Redirect to landing page if no subscription exists
        return redirect('landingpage')




@login_required
def my_subscription(request):
    """
    View the current active subscription.
    """
    subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    return render(request, 'my_subscription.html', {'subscription': subscription})

def create_post(request):
    subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save tags
            return redirect('blog_listings')
    else:
        form = BlogPostForm()
    
    return render(request, 'post_form.html', {'form': form,'User_Subscription': subscription})

def blog_listings(request):
    subscription = UserSubscription.objects.filter(user=request.user, active=True).first()

    tag = request.GET.get('tag')  # Get tag from URL
    if tag:
        posts = BlogPost.objects.filter(tags__name=tag)  # Filter posts by tag
    else:
        posts = BlogPost.objects.all()  # Get all posts

    print(posts)
    # Fetch top-level comments for the retrieved posts
    # comments = Comment.objects.filter(post__in=posts, parent=None, approved=True)
    # Attach comments to each post
    # Annotate each post with the count of approved top-level comments
    posts = posts.annotate(comment_count=Count('comments', filter=Q(comments__parent=None, comments__approved=True)))

    return render(request, "blog_listing.html", {
        'posts': posts,
        'User_Subscription': subscription,
    })


def blog_post(request,post_id):
    subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.filter(parent=None, approved=True)  # Only top-level comments
    form = CommentForm()
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            parent_id = request.POST.get("parent_id")
            if parent_id:  
                comment.parent = Comment.objects.get(id=parent_id)  # Set parent comment
            comment.save()
            return redirect('blog_post', post_id=post.id)
    return render(request,"blog_post.html", {'post': post, 'comments': comments, 'form': form,'User_Subscription': subscription})


def faq(request):
    return render(request,"faq.html")



@login_required
def logout_view(request):
    logout(request)
    return redirect('landingpage')