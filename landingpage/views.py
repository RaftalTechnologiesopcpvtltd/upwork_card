from django.shortcuts import render, redirect, get_object_or_404 ,reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import razorpay
import uuid

import logging
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count , Q
from django.http import JsonResponse
import stripe
from datetime import datetime
import ast
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
import decimal
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import csv
from django.http import HttpResponse
import ast
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import UserSubscription, MyListing, Product

stripe.api_key = settings.STRIPE_SECRET_KEY


def Landing_page(request):
    faqs = FAQ.objects.all()
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
        "faqs" : faqs,
        "User_Subscription" : User_Subscription,
        "slidders" : slidders,
        "Contact" : Contact,
        "Pricings" :Pricings
    }

    return render(request, 'home.html',context)




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


def register_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data['username'] = data['email']
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            login(request, user)
            return redirect('login')
        else:
            # print("Form is invalid")
            print(form.errors.as_data())  # Print detailed form errors
            messages.error(request, "Unsuccessful registration. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def subscribe_to_plan(request, plan_id):
    """
    Subscribe to a pricing plan.
    """
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")
    
    plan = get_object_or_404(Pricing, id=plan_id)

    subscription_prod = {
        'Monthly' : 'price_1QtpecKyDQNgXXcfn7iWYSRF',
        'Yearly' : 'price_1Qtpk3KyDQNgXXcfzS4EApeg',
    }
    try:
        active_subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        active_subscription = None
    
    if request.method == 'POST':
        price_id = request.POST.get('price_id')
        print("Price id : ",price_id)
        subscription_id = subscription_prod.get(price_id)
        print(subscription_id)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=request.user.email,
            line_items=[{"price": subscription_id, "quantity": 1}],
            success_url=f"{request.scheme}://{request.get_host()}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.scheme}://{request.get_host()}/payment-failed/",
            metadata={
                "user_id" : request.user.id,
            }
        )
        if active_subscription:
            active_subscription.user=request.user
            active_subscription.session_id = checkout_session.id
            active_subscription.plan=plan
            active_subscription.active=False
            active_subscription.save() 
        else:
            UserSubscription.objects.create(
            user=request.user,
            session_id = checkout_session.id,
            plan=plan,
            active=False
            )
        return redirect(checkout_session.url, code=303)

    context = {
        # 'subscription' : subscription,
        'plan': plan,
        'amount': plan.price,  # Amount in paise
    }

    return render(request, 'payment_checkout.html', context)

@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        return render(request, "paymentfail.html", {"error": "Session ID is missing."})

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user_id = session.metadata.get("user_id", None)

        if not user_id:
            return render(request, "paymentfail.html", {"error": "Invalid session metadata."})

        user = CustomUser.objects.get(id=user_id)
        subscription_info = stripe.Subscription.retrieve(session.subscription)
        price = subscription_info['items']['data'][0]['price']
        product_id = price['product']
        product = stripe.Product.retrieve(product_id)

        # Update subscription status in database
        subscription_id = session.subscription
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

        customer_id = session.customer

        subscription = UserSubscription.objects.get(session_id=session_id)
        subscription.active = True
        subscription.subscription_id = subscription_id
        subscription.customer_id = customer_id
        subscription.payment_status = 'captured'
        subscription.interval = price['recurring']['interval']
        subscription.start_date = datetime.fromtimestamp(int(subscription_info['current_period_start']))
        subscription.end_date = datetime.fromtimestamp(int(subscription_info['current_period_end']))  # ✅ Fixed key

        subscription.save()

        return render(request, "subscription_success.html", {"subscription_id": subscription_id})

    except stripe.error.StripeError as e:
        return render(request, "paymentfail.html", {"error": str(e)})

    except UserSubscription.DoesNotExist:
        return render(request, "paymentfail.html", {"error": "Subscription record not found."})

    except CustomUser.DoesNotExist:
        return render(request, "paymentfail.html", {"error": "User not found."})


def payment_failed(request):
    return render(request, "paymentfail.html")

import requests
import json

def prod_API(query, scrapers, location=None):
    req_url = "http://3.141.5.147:8000/api/scrape/"
    
    headers = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json"
    }

    if location:
        payload = json.dumps({
            "query": query,
            "location":location,
            "scrapers": scrapers
        })
    else:
        payload = json.dumps({
        "query": query,
        "scrapers": scrapers,
        })

    try:
        response = requests.post(req_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)
        return response.json()  # Return JSON if successful
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None  # Return None if there's an error

def sort_products(products):
    def get_price(product):
        if product.get("selling_type") == "Auction":
            price = product.get("current_bid_price")
        else:
            price = product.get("product_price")
        try:
            return float(price)
        except (ValueError, TypeError):
            return 0.0
    return sorted(products, key=get_price)


def clean_price(value):
    if isinstance(value, str):
        # Remove $ and commas, strip spaces
        value = value.replace('$', '').replace(',', '').strip()
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def product_search(request):
    
    query = request.GET.get("query", "").strip()
    location = request.GET.get("location", "").strip()
    marketplace = request.GET.get("marketplace", "").strip()
    scrapers = [marketplace]
    print(query)
    print(location)
    print(marketplace)
    print(scrapers)
    resp = prod_API(query, scrapers, location)
    results = []
    today = datetime.now().date()
    all_prod_data = []

# Debugging: Check the type of resp['data']
    data = resp.get('data', {})

    if not isinstance(data, dict):
        print(f"Error: Expected a dictionary for 'data', but got {type(data)} instead.")
        print("Full response:", resp)  # Print full response for debugging
        data = {}  # Ensure 'data' is always a dictionary

    try:
        if 'all' in marketplace:
            ebay = data.get('ebay', [])  # Default to empty list if missing
            fivemiles = data.get('fivemiles', [])
            fanatic = data.get('fanatic', [])
            facebook = data.get('facebook', [])
            craigslist = data.get('craigslist', [])
            mercari = data.get('mercari', [])
            # offerup = data.get('offerup', [])
            all_prod_data = ebay + fivemiles + fanatic + facebook + craigslist + mercari 
            # all_prod_data = ebay + fivemiles + fanatic + facebook + craigslist + mercari + offerup
        elif 'fivemiles' in marketplace:
            all_prod_data = data.get('fivemiles', [])
        elif 'fanatic' in marketplace:
            all_prod_data = data.get('fanatic', [])
        elif 'ebay' in marketplace:
            all_prod_data = data.get('ebay', [])
        elif 'facebook' in marketplace:
            all_prod_data = data.get('facebook', [])
        elif 'mercari' in marketplace:
            all_prod_data = data.get('mercari', [])
        elif 'craigslist' in marketplace:
            all_prod_data = data.get('craigslist', [])
        elif 'offerup' in marketplace:
            all_prod_data = data.get('offerup', [])
    except Exception as e:
        print(f"Unexpected error accessing marketplace data: {e}")
        all_prod_data = []


    for p in all_prod_data:
        product_images_list = p.get("Product Images")
        # print(product_images_list)

        
        results.append({
            "id": str(uuid.uuid4()),  # Manually generated unique ID
            "website_name": p.get("Website Name"),
            "website_url": p.get("Website URL"),
            "product_link": p.get("Product Link"),
            "product_images": product_images_list if product_images_list else [],  # Handle missing images
            "selling_type": p.get("Selling Type"),
            "product_title": p.get("Product Title"),
            "product_price_currency": p.get("Product Price Currency"),
            "product_price": clean_price(p.get("Product Price")),
            "current_bid_price": clean_price(str(p.get("Current Bid Price")) if p.get("Current Bid Price") else "N/A"),
            "current_bid_currency": p.get("Current Bid Currency"),
            "current_bid_count": p.get("Current Bid Count"),
            "description": p.get("Description"),
            "condition": p.get("Condition"),
            "condition_id": p.get("Condition Id"),
            "condition_descriptors": p.get("Condition Descriptors"),
            "condition_values": p.get("Condition Values"),
            "condition_additional_info": p.get("Condition Additional Info"),
            "product_availability_status": p.get("Product Availibility status"),
            "product_availability_quantity": p.get("Product Availibility Quantity"),
            "product_sold_quantity": p.get("Product Sold Quantity"),
            "product_remaining_quantity": p.get("Product Remaining Quantity"),
            "shipping_cost": p.get("Shipping Cost"),
            "shipping_currency": p.get("Shipping Currency"),
            "shipping_service_code": p.get("Shipping Service Code"),
            "shipping_carrier_code": p.get("Shipping Carrier Code"),
            "shipping_type": p.get("Shipping Type"),
            "additional_shipping_cost_per_unit": p.get("Additional Shipping Cost Per Unit"),
            "additional_shipping_cost_currency": p.get("Additional Shipping Cost Currency"),
            "shipping_cost_type": p.get("Shipping Cost Type"),
            "estimated_arrival": p.get("Estimated Arrival"),
            "brand": p.get("Brand"),
            "category": p.get("Category"),
            "updated": p.get("Updated"),
            "auction_id": p.get("Auction Id"),
            "bid_count": p.get("Bid Count"),
            "certified_seller": p.get("Certified Seller"),
            "favorited_count": p.get("Favorited Count"),
            "highest_bidder": p.get("Highest Bidder"),
            "listing_id": p.get("Listing Id"),
            "integer_id": p.get("Integer Id"),
            "is_owner": p.get("Is Owner"),
            "listing_type": p.get("Listing Type"),
            "lot_string": p.get("Lot String"),
            "slug": p.get("Slug"),
            "starting_price": p.get("Starting Price"),
            "starting_price_currency": p.get("Starting Price Currency"),
            "is_closed": p.get("Is Closed"),
            "user_bid_status": p.get("User Bid Status"),
            "user_max_bid": p.get("User Max Bid"),
            "status": p.get("Status"),
            "return_terms_returns_accepted": p.get("ReturnTerms returns Accepted"),
            "return_terms_refund_method": p.get("ReturnTerms refund Method"),
            "return_terms_return_shipping_cost_payer": p.get("ReturnTerms return Shipping Cost Payer"),
            "return_terms_return_period_value": p.get("ReturnTerms return Period Value"),
            "return_terms_return_period_unit": p.get("ReturnTerms return Period Unit"),
            "payment_methods": p.get("Payment Methods"),
            "quantity_used_for_estimate": p.get("Quantity Used For Estimate"),
            "min_estimated_delivery_date": p.get("Min Estimated Delivery Date"),
            "max_estimated_delivery_date": p.get("Max Estimated Delivery Date"),
            "buying_options": p.get("Buying Options"),
            "minimum_price_to_bid": p.get("Minimum Price to Bid"),
            "minimum_price_currency": p.get("Minimum Price Currency"),
            "unique_bidder_count": p.get("Unique Bidder Count"),
            "owner_location": p.get("Owner Location"),
            "date": today
        })
    # print(results)
    results = sort_products(results)

    return JsonResponse({"products": results})

@login_required
def fav_view(request):
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except:
        subscription = None
    fav_products = Favourites.objects.filter(user=request.user)
    fav_results = []
    for fav_prod in fav_products:
        product_images_list = []
        if fav_prod.product.product_images:
            try:
                product_images_list = ast.literal_eval(fav_prod.product.product_images)
                if not isinstance(product_images_list, list):  # Ensure it's a list
                    product_images_list = []
            except (SyntaxError, ValueError):
                product_images_list = []
        fav_results.append({
            "id": fav_prod.id,
            "title": fav_prod.product.product_title,
            "link": fav_prod.product.product_link,
            "selling_type": fav_prod.product.selling_type,
            "website_name": fav_prod.product.website_name,
            "price": fav_prod.product.product_price,
            "current_bid_price": str(fav_prod.product.current_bid_price) if fav_prod.product.current_bid_price else "N/A",
            "current_bid_currency": fav_prod.product.current_bid_currency,
            "current_bid_count": fav_prod.product.current_bid_count,
            "image": product_images_list[0] if product_images_list else "",  # Handle missing images
            "decscription" : fav_prod.product.description,
        })
    return render(request, 'favourites.html',{"fav_products":fav_results,"User_Subscription" : subscription})

def get_product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Convert `product_images` field (string) to a list
    product_images_list = []
    if product.product_images:
        try:
            product_images_list = ast.literal_eval(product.product_images)
            if not isinstance(product_images_list, list):  # Ensure it's a list
                product_images_list = []
        except (SyntaxError, ValueError):
            product_images_list = []

    # Convert `condition_descriptors`, `condition_values`, `payment_methods`, and `buying_options` to lists if stored as strings
    condition_descriptors_list = product.condition_descriptors.split(",") if product.condition_descriptors else []
    condition_values_list = product.condition_values.split(",") if product.condition_values else []
    payment_methods_list = product.payment_methods.split(",") if product.payment_methods else []
    buying_options_list = product.buying_options.split(",") if product.buying_options else []

    # Convert Decimal fields to string to avoid JSON serialization errors
    product_data = {
        "id": product.id,
        "website_name": product.website_name,
        "website_url": product.website_url,
        "product_link": product.product_link,
        "product_title": product.product_title,
        "product_images": product_images_list,
        "product_price": str(product.product_price) if product.product_price else "N/A",
        "product_price_currency": product.product_price_currency,
        "selling_type": product.selling_type,
        "current_bid_price": str(product.current_bid_price) if product.current_bid_price else "N/A",
        "current_bid_currency": product.current_bid_currency,
        "current_bid_count": product.current_bid_count,
        "description": product.description,
        "condition": product.condition,
        "condition_id": product.condition_id,
        "condition_descriptors": condition_descriptors_list,
        "condition_values": condition_values_list,
        "condition_additional_info": product.condition_additional_info,
        "product_availability_status": product.product_availability_status,
        "product_availability_quantity": product.product_availability_quantity,
        "product_sold_quantity": product.product_sold_quantity,
        "product_remaining_quantity": product.product_remaining_quantity,
        "shipping_cost": str(product.shipping_cost) if product.shipping_cost else "N/A",
        "shipping_currency": product.shipping_currency,
        "shipping_service_code": product.shipping_service_code,
        "shipping_carrier_code": product.shipping_carrier_code,
        "shipping_type": product.shipping_type,
        "additional_shipping_cost_per_unit": str(product.additional_shipping_cost_per_unit) if product.additional_shipping_cost_per_unit else "N/A",
        "additional_shipping_cost_currency": product.additional_shipping_cost_currency,
        "shipping_cost_type": product.shipping_cost_type,
        "estimated_arrival": product.estimated_arrival,
        "brand": product.brand,
        "category": product.category,
        "updated": product.updated,
        "auction_id": product.auction_id,
        "bid_count": product.bid_count,
        "certified_seller": product.certified_seller,
        "favorited_count": product.favorited_count,
        "highest_bidder": product.highest_bidder,
        "listing_id": product.listing_id,
        "integer_id": product.integer_id,
        "is_owner": product.is_owner,
        "listing_type": product.listing_type,
        "lot_string": product.lot_string,
        "slug": product.slug,
        "starting_price": str(product.starting_price) if product.starting_price else "N/A",
        "starting_price_currency": product.starting_price_currency,
        "is_closed": product.is_closed,
        "user_bid_status": product.user_bid_status,
        "user_max_bid": str(product.user_max_bid) if product.user_max_bid else "N/A",
        "status": product.status,
        "return_terms_returns_accepted": product.return_terms_returns_accepted,
        "return_terms_refund_method": product.return_terms_refund_method,
        "return_terms_return_shipping_cost_payer": product.return_terms_return_shipping_cost_payer,
        "return_terms_return_period_value": product.return_terms_return_period_value,
        "return_terms_return_period_unit": product.return_terms_return_period_unit,
        "payment_methods": payment_methods_list,
        "quantity_used_for_estimate": product.quantity_used_for_estimate,
        "min_estimated_delivery_date": product.min_estimated_delivery_date,
        "max_estimated_delivery_date": product.max_estimated_delivery_date,
        "buying_options": buying_options_list,
        "minimum_price_to_bid": str(product.minimum_price_to_bid) if product.minimum_price_to_bid else "N/A",
        "minimum_price_currency": product.minimum_price_currency,
        "unique_bidder_count": product.unique_bidder_count,
    }

    return JsonResponse(product_data, safe=False)




@login_required
def dashboard_view(request):
    """
    Dashboard view for users with an active subscription.
    """
    slidders = Slidder.objects.all()
    today = now().date()
    try:
        # Fetch all products
        products = Product.objects.all()
        # List to store all products with formatted images
        All_brands = []

        # Loop through each product
        for product in products:
            # Append to list
            All_brands.append(product.website_name)
            
        print(set(All_brands))
        subscription = UserSubscription.objects.get(user=request.user)
        stripe_sub = stripe.Subscription.retrieve(subscription.subscription_id)
        
        if stripe_sub.status in ["canceled", "past_due", "unpaid"] or subscription.end_date <= today:
            subscription.active = False
            subscription.save(update_fields=['active'])
            print(f"Subscription {subscription.id} deactivated")
            
        if subscription.active:
            # Render the dashboard page if the subscription is active
            return render(request, 'dashboard.html',{"slidders" : slidders,"marketplaces":list(set(All_brands)),"User_Subscription" : subscription,"today":today})  # Replace with your dashboard template
        else:
            # Redirect to landing page if the subscription is not active
            return redirect('landingpage')
    except UserSubscription.DoesNotExist:
        # Redirect to landing page if no subscription exists
        return redirect('landingpage')

@login_required
def profile(request):
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        return render(request, 'profile.html',{"User_Subscription" : subscription})
    except:
        subscription = None
    return render(request, 'profile.html')

@login_required
def my_subscription(request):
    """
    View the current active subscription.
    """
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")
    # stripe_subscription = stripe.Subscription.retrieve(subscription.subscription_id)
    # print(stripe_subscription)
    return render(request, 'my_subscription.html', {'User_Subscription': subscription})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    print("endpoint_secret :",endpoint_secret)

    print("Received Webhook:", payload)
    print("Received Stripe Signature Header:", sig_header)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle subscription events
    if event["type"] in ["customer.Subscription.retrieve"]:
        subscription_data = event["data"]["object"]
        stripe_subscription_id = subscription_data["id"]
        status = subscription_data["status"]  # active, canceled, past_due, etc.

        # Find and cancel the subscription in Django
        subscription = UserSubscription.objects.filter(stripe_subscription_id=stripe_subscription_id).first()
        if subscription and status in ["canceled", "past_due", "unpaid"]:
            subscription.active = False
            subscription.save(update_fields=['active'])
            print(f"Subscription {stripe_subscription_id} marked as inactive")

    return JsonResponse({"status": "success"})


@login_required
def create_post(request):
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")
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


@login_required
def blog_listings(request):
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")

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

@login_required
def blog_post(request,post_id):
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")
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
    faqs = FAQ.objects.all()
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except:
        subscription = None

    return render(request,"faq.html",{'faqs': faqs,'User_Subscription': subscription})


def cancel_subscription(request):
    try:
        subscription_id = request.POST.get("subscription_id")
        cancel_now = request.POST.get("cancel_now", False)  # Default: Cancel at end of period
        subscription = UserSubscription.objects.filter(user=request.user, subscription_id=subscription_id)

        print("subscription_id :",subscription_id)
        print("cancel_now: ",cancel_now)

        if cancel_now:
            stripe.Subscription.delete(subscription_id)  # Cancel Immediately
            subscription.delete()
            print(subscription)
            return redirect("my_subscription")
        else:
            stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)  # Cancel at end
            return redirect("my_subscription")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def resume_subscription(request):
    try:
        subscription_id = request.POST.get("subscription_id")

        stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)

        return JsonResponse({"message": "Subscription resumed successfully."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def update_subscription(request):
    try:
        subscription_prod = {
            'Yearly' : 'price_1Qtpk3KyDQNgXXcfzS4EApeg',
        }
        subscriptionId = request.POST.get("subscription_id")
        stripe_subscription = stripe.Subscription.retrieve(subscriptionId)
        subscription_id = stripe_subscription.get('items').get('data')[0].get('id')
        Pricings = Pricing.objects.filter(price_heading="Yearly").first()
        print(Pricings)

        plan = request.POST.get("plan")
        print("subscription_id :",subscription_id)
        price_id = subscription_prod.get(plan)
        print("plan: ",plan)
        print("price_id: ",price_id)

        subscription = stripe.SubscriptionItem.modify(
            subscription_id,
            price=price_id,  # New price ID
            payment_behavior="allow_incomplete",  # Handle failed payments
            proration_behavior="create_prorations",  # Adjust billing for changes
        )
        subscription_info = stripe.Subscription.retrieve(subscriptionId)
        subscription = UserSubscription.objects.get(subscription_id=subscriptionId)
        subscription.plan = Pricings
        price = subscription_info['items']['data'][0]['price']
        product_id = price['product']
        subscription.interval = price['recurring']['interval']
        subscription.start_date = datetime.fromtimestamp(int(subscription_info['current_period_start']))
        subscription.end_date = datetime.fromtimestamp(int(subscription_info['current_period_end']))  # ✅ Fixed key

        subscription.save()

        return redirect("my_subscription")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def check_unpaid_invoices(request):
    try:
        customer_id = request.GET.get("customer_id",'cus_RnQlbssw0HORXa')

        invoices = stripe.Invoice.list(customer=customer_id)
        # unpaid_invoices = [{"id": inv.id, "amount_due": inv.amount_due} for inv in invoices]
        unpaid_invoices = invoices

        return JsonResponse({"unpaid_invoices": unpaid_invoices})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def process_refund(request):
    try:
        charge_id = request.POST.get("charge_id")
        amount = int(request.POST.get("amount"))  # Amount in cents

        refund = stripe.Refund.create(charge=charge_id, amount=amount)

        return JsonResponse({"message": "Refund processed successfully.", "refund_id": refund.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def logout_view(request):
    logout(request)
    return redirect('landingpage')




# @login_required
# def bulk_upload_products(request):
#     try:
#         subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
#     except Exception as e:
#         print(f"Subscription check failed: {e}")
#         subscription = None

#     if not (subscription and subscription.active):
#         return redirect("landingpage")

#     if request.method == "POST":
#         form = CSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES["csv_file"]
#             if not csv_file.name.endswith(".csv"):
#                 messages.error(request, "File is not a CSV!")
#                 return redirect("bulk_upload_products")

#             try:
#                 decoded_file = csv_file.read().decode("utf-8", errors="ignore").splitlines()
#                 reader = csv.DictReader(decoded_file)
#             except Exception as e:
#                 messages.error(request, f"Error reading CSV file: {e}")
#                 return redirect("bulk_upload_products")

#             required_columns = {
#                 "Website Name",
#                 "Website URL",
#                 "Product Link",
#                 "Product Images",
#                 "Selling Type",
#                 "Product Title",
#                 "Product Price Currency",
#                 "Product Price",
#                 "Current Bid Price",
#                 "Current Bid Currency",
#                 "Current Bid Count",
#                 "Description",
#                 "Condition",
#                 "Condition Id",
#                 "Condition Descriptors",
#                 "Condition Values",
#                 "Condition Additional Info",
#                 "Product Availibility status",
#                 "Product Availibility Quantity",
#                 "Product Sold Quantity",
#                 "Product Remaining Quantity",
#                 "Shipping Cost",
#                 "Shipping Currency",
#                 "Shipping Service Code",
#                 "Shipping Carrier Code",
#                 "Shipping Type",
#                 "Additional Shipping Cost Per Unit",
#                 "Additional Shipping Cost Currency",
#                 "Shipping Cost Type",
#                 "Estimated Arrival",
#                 "Brand",
#                 "Category",
#                 "Updated",
#                 "Auction Id",
#                 "Bid Count",
#                 "Certified Seller",
#                 "Favorited Count",
#                 "Highest Bidder",
#                 "Listing Id",
#                 "Integer Id",
#                 "Is Owner",
#                 "Listing Type",
#                 "Lot String",
#                 "Slug",
#                 "Starting Price",
#                 "Starting Price Currency",
#                 "Is Closed",
#                 "User Bid Status",
#                 "User Max Bid",
#                 "Status",
#                 "ReturnTerms returns Accepted",
#                 "ReturnTerms refund Method",
#                 "ReturnTerms return Shipping Cost Payer",
#                 "ReturnTerms return Period Value",
#                 "ReturnTerms return Period Unit",
#                 "Payment Methods",
#                 "Quantity Used For Estimate",
#                 "Min Estimated Delivery Date",
#                 "Max Estimated Delivery Date",
#                 "Buying Options",
#                 "Minimum Price to Bid",
#                 "Minimum Price Currency",
#                 "Unique Bidder Count",
#             }

#             actual_columns = set(reader.fieldnames)
#             missing_columns = required_columns - actual_columns
#             if missing_columns:
#                 messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
#                 return redirect("bulk_upload_products")

#             def safe_int(value, default=0):
#                 try:
#                     return int(float(value)) if value else default
#                 except (ValueError, TypeError):
#                     return default

#             def safe_decimal(value):
#                 try:
#                     return decimal.Decimal(value.replace("$", "").replace(",", "")) if value else None
#                 except (decimal.InvalidOperation, ValueError, AttributeError):
#                     return None

#             def safe_bool(value):
#                 return str(value).strip().lower() in ["true", "1", "yes"]

#             def safe_date(value):
#                 if not value or value.strip().lower() in ["", "none", "null"]:
#                     return None
#                 try:
#                     return datetime.strptime(value.strip(), "%Y-%m-%d").date()
#                 except ValueError:
#                     return None

#             product_list = []
#             for row in reader:
#                 try:
#                     product = MyListing(
#                         user=request.user,
#                         website_name=row.get("Website Name"),
#                         website_url=row.get("Website URL"),
#                         product_link=row.get("Product Link"),
#                         product_title=row.get("Product Title"),
#                         product_images=row.get("Product Images"),
#                         selling_type=row.get("Selling Type"),
#                         product_price=safe_decimal(row.get("Product Price")),
#                         product_price_currency=row.get("Product Price Currency"),
#                         current_bid_price=safe_decimal(row.get("Current Bid Price")),
#                         current_bid_currency=row.get("Current Bid Currency", "USD"),
#                         current_bid_count=safe_int(row.get("Current Bid Count")),
#                         description=row.get("Description"),
#                         condition=row.get("Condition"),
#                         condition_id=row.get("Condition Id"),
#                         condition_descriptors=row.get("Condition Descriptors"),
#                         condition_values=row.get("Condition Values"),
#                         condition_additional_info=row.get("Condition Additional Info"),
#                         product_availability_status=row.get("Product Availibility status"),
#                         product_availability_quantity=safe_int(row.get("Product Availibility Quantity")),
#                         product_sold_quantity=safe_int(row.get("Product Sold Quantity")),
#                         product_remaining_quantity=safe_int(row.get("Product Remaining Quantity")),
#                         shipping_cost=safe_decimal(row.get("Shipping Cost")),
#                         shipping_currency=row.get("Shipping Currency", "USD"),
#                         shipping_service_code=row.get("Shipping Service Code"),
#                         shipping_carrier_code=row.get("Shipping Carrier Code"),
#                         shipping_type=row.get("Shipping Type"),
#                         additional_shipping_cost_per_unit=safe_decimal(row.get("Additional Shipping Cost Per Unit")),
#                         additional_shipping_cost_currency=row.get("Additional Shipping Cost Currency", "USD"),
#                         shipping_cost_type=row.get("Shipping Cost Type"),
#                         estimated_arrival=row.get("Estimated Arrival"),
#                         brand=row.get("Brand"),
#                         category=row.get("Category"),
#                         auction_id=row.get("Auction Id"),
#                         bid_count=safe_int(row.get("Bid Count")),
#                         certified_seller=safe_bool(row.get("Certified Seller")),
#                         favorited_count=safe_int(row.get("Favorited Count")),
#                         highest_bidder=row.get("Highest Bidder"),
#                         listing_id=row.get("Listing Id"),
#                         integer_id=safe_int(row.get("Integer Id")),
#                         is_owner=safe_bool(row.get("Is Owner")),
#                         listing_type=row.get("Listing Type"),
#                         lot_string=row.get("Lot String"),
#                         slug=row.get("Slug"),
#                         starting_price=safe_decimal(row.get("Starting Price")),
#                         starting_price_currency=row.get("Starting Price Currency", "USD"),
#                         is_closed=safe_bool(row.get("Is Closed")),
#                         user_bid_status=row.get("User Bid Status"),
#                         user_max_bid=safe_decimal(row.get("User Max Bid")),
#                         status=row.get("Status"),
#                     )
#                     product_list.append(product)
#                 except Exception as e:
#                     print(f"Skipping row due to error: {e}")

#             if product_list:
#                 MyListing.objects.bulk_create(product_list)
#                 messages.success(request, "Products uploaded successfully!")
#             else:
#                 messages.error(request, "No valid products found to upload.")

#             return redirect("bulk_upload_products")

#     form = CSVUploadForm()
#     return render(request, "bulk_upload.html", {"form": form,'User_Subscription': subscription})

# @require_POST
@login_required
def add_to_favourites(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Favourites.objects.get_or_create(user=request.user, product=product)
    
    if created:
        return JsonResponse({'status': 'success', 'message': 'Product added to wishlist'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Product already in wishlist'})

@csrf_exempt
@login_required
def remove_from_favourites(request):
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('product_id')
        print(wishlist_item_id)
        wishlist_item = get_object_or_404(Favourites, id=wishlist_item_id, user=request.user)
        wishlist_item.delete()
        return JsonResponse({'status': 'success', 'message': 'Product removed from wishlist'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def download_csv_template(request):
    # Define the CSV headers based on your expected format
    header = ["Product Title"]

    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_template.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header to the CSV file
    writer.writerow(header)

    return response

@login_required
def bulk_upload_products(request):
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "File is not a CSV!")
                return redirect("bulk_upload_products")

            try:
                decoded_file = csv_file.read().decode("utf-8", errors="ignore").splitlines()
                reader = csv.DictReader(decoded_file)
            except Exception as e:
                messages.error(request, f"Error reading CSV file: {e}")
                return redirect("bulk_upload_products")

            required_columns = {
                "Product Title"
            }

            actual_columns = set(reader.fieldnames)
            missing_columns = required_columns - actual_columns
            if missing_columns:
                messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
                return redirect("bulk_upload_products")


            product_list = []
            for row in reader:
                try:
                    product = MyListing(
                        user=request.user,
                        product_title=row.get("Product Title"),
                    )
                    product_list.append(product)
                except Exception as e:
                    print(f"Skipping row due to error: {e}")

            if product_list:
                MyListing.objects.bulk_create(product_list)
                messages.success(request, "Products uploaded successfully!")
            else:
                messages.error(request, "No valid products found to upload.")

            return redirect("bulk_upload_products")

    form = CSVUploadForm()
    return render(request, "bulk_upload.html", {"form": form,'User_Subscription': subscription})


@login_required
def my_products(request):
    try:
        subscription = UserSubscription.objects.filter(user=request.user, active=True).first()
    except Exception as e:
        print(f"Subscription check failed: {e}")
        subscription = None

    if not (subscription and subscription.active):
        return redirect("landingpage")

    # Get the product titles as a list of strings
    my_products = list(MyListing.objects.filter(user=request.user).values_list("product_title", flat=True))

    product_results = []

    if my_products:  # Ensure there are products to filter
        query_filter = Q()
        for title in my_products:
            if title:
                query_filter |= Q(product_title__icontains=title)  # OR condition for multiple titles

        products = Product.objects.filter(query_filter)  # Query products only once

        # Build results
        for p in products:
            product_images_str = p.product_images

            if product_images_str:
                try:
                    product_images_list = ast.literal_eval(product_images_str)  # Convert string to list
                    if not isinstance(product_images_list, list):
                        product_images_list = []
                except (SyntaxError, ValueError):
                    product_images_list = []
            else:
                product_images_list = []

            product_results.append({
                "id": p.id,
                "title": p.product_title,
                "link": p.product_link,
                "selling_type": p.selling_type,
                "website_name": p.website_name,
                "price": p.product_price,
                "current_bid_price": str(p.current_bid_price) if p.current_bid_price else "N/A",
                "current_bid_currency": p.current_bid_currency,
                "current_bid_count": p.current_bid_count,
                "image": product_images_list[0] if product_images_list else "",  # Handle missing images
                "date": p.updated,
            })

    return render(request, "myproducts.html", {"User_Subscription": subscription, "product_results": product_results})
import boto3
import paramiko
import time
import os
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

def server_page(request):
    return render(request, 'server_page.html')

def run_scripts_on_aws(request):
    if request.method == 'POST':
        aws_access_key = os.getenv('AWS_ACCESS_KEY')
        aws_secret_key = os.getenv('AWS_SECRET_KEY')
        region = os.getenv('AWS_REGION')
        ami_id = os.getenv('AMI_ID')
        instance_type = os.getenv('INSTANCE_TYPE')
        key_name = os.getenv('KEY_NAME')
        security_group = os.getenv('SECURITY_GROUP')
        private_key_path = os.getenv('PRIVATE_KEY_PATH')

        try:
            ec2 = boto3.client(
                'ec2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )

            # Start EC2 instance
            response = ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                KeyName=key_name,
                SecurityGroups=[security_group]
            )

            instance_id = response['Instances'][0]['InstanceId']

            ec2_resource = boto3.resource(
                'ec2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )

            instance = ec2_resource.Instance(instance_id)
            instance.wait_until_running()
            instance.load()

            public_ip = instance.public_ip_address

            # SSH connection to the instance
            key = paramiko.RSAKey.from_private_key_file(private_key_path)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=public_ip, username='ec2-user', pkey=key)

            # Run command on the instance
            stdin, stdout, stderr = client.exec_command('echo "Hello from AWS EC2!"')
            output = stdout.read().decode('utf-8')

            client.close()

            # Stop the instance after use
            ec2.stop_instances(InstanceIds=[instance_id])

            return JsonResponse({
                'status': 'Success',
                'instance_id': instance_id,
                'output': output
            })

        except Exception as e:
            return JsonResponse({'status': 'Failed', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'Invalid request'}, status=400)