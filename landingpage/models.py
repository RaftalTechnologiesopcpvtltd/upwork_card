from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from datetime import timedelta
from datetime import date
from taggit.managers import TaggableManager  # Import taggit
import stripe
from django.conf import settings

from django.db import models

class Product(models.Model):
    website_name = models.CharField(max_length=255, null=True)
    website_url = models.URLField(null=True)
    product_link = models.URLField(null=True)
    product_title = models.CharField(max_length=255, null=True)
    product_images = models.TextField(null=True)  # A field to store image URLs as a comma-separated string
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_availability_status = models.CharField(max_length=100, null=True)
    product_availability_quantity = models.IntegerField(null=True)
    product_sold_quantity = models.IntegerField(null=True)
    product_remaining_quantity = models.IntegerField(null=True)
    description = models.TextField(null=True)
    shipping = models.CharField(max_length=255, null=True)
    est_arrival = models.CharField(max_length=255,null=True)
    condition = models.CharField(max_length=255, null=True)
    condition_id = models.CharField(max_length=100, null=True)
    condition_descriptors = models.TextField(null=True)  # Using TextField to store descriptors as a string
    condition_values = models.TextField(null=True)  # Using TextField to store values as a string
    condition_additional_info = models.TextField(null=True)
    brand = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    updated = models.CharField(max_length=255,null=True)
    auction_id = models.CharField(max_length=100, null=True)
    bid_count = models.IntegerField(null=True)
    certified_seller = models.CharField(max_length=100,null=True)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_bid_currency = models.CharField(max_length=10, null=True)
    favorited_count = models.IntegerField(null=True)
    highest_bidder = models.CharField(max_length=255, null=True)
    listing_id = models.CharField(max_length=100, null=True)
    integer_id = models.IntegerField(null=True)
    is_owner = models.CharField(max_length=100,null=True)
    listing_type = models.CharField(max_length=100, null=True)
    lot_string = models.CharField(max_length=100, null=True)
    slug = models.SlugField(null=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    starting_price_currency = models.CharField(max_length=10, null=True)
    is_closed = models.CharField(max_length=100,null=True)
    user_bid_status = models.CharField(max_length=100, null=True)
    user_max_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=100, null=True)
    return_terms_returns_accepted = models.CharField(max_length=100,null=True)
    return_terms_refund_method = models.CharField(max_length=100, null=True)
    return_terms_return_shipping_cost_payer = models.CharField(max_length=100, null=True)
    return_terms_return_period_value = models.IntegerField(null=True)
    return_terms_return_period_unit = models.CharField(max_length=50, null=True)
    payment_methods = models.TextField(null=True)  # Store payment methods as a comma-separated string

    def __str__(self):
        return self.product_title


class CustomUser(AbstractUser):
    GENDER_CHOICES =(
        ('male','Male'),
        ('female','Female'),
    ('prefer not to say','Prefer Not to Say'),
    )
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    category = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=20,choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True,default='')
    city = models.CharField(max_length=100,blank=True,default='')
    country = models.CharField(max_length=100,blank=True,default='')
    zip_code = models.CharField(max_length=20,blank=True,default='')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# Create your models here.
class Slidder(models.Model):
    image = models.ImageField(upload_to='slidder/')
    heading = models.CharField(max_length=100)
    text=models.TextField()
    
    def __str__(self):
        return self.heading
    


class Pricing(models.Model):
    price_heading = models.CharField(max_length=100)
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    desc = models.TextField()
    duration_in_days = models.PositiveIntegerField(default=30)
    price_feature1 = models.CharField(max_length=100 ,default = "")
    price_feature2 = models.CharField(max_length=100 ,default = "")
    price_feature3 = models.CharField(max_length=100 ,default = "")
    price_feature4 = models.CharField(max_length=100 ,default = "")

    def __str__(self):
        return self.price_heading


class Contactus(models.Model):
    about = models.TextField()
    company_address = models.TextField()
    company_phone = models.CharField(max_length=20)
    company_email = models.EmailField()

    def __str__(self):
        return self.company_email
    

class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Pricing, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    subscription_id = models.CharField(max_length=100, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=20, null=True, blank=True)
    interval = models.CharField(max_length=50, default="month")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        # 🔹 Check if the subscription has ended
        if self.end_date and now().date() >= self.end_date:
            return False  # Mark inactive if end date has passed

        # 🔹 Also check Stripe for real-time subscription status
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
            if subscription.status in ["canceled", "past_due", "unpaid"]:
                return False  # Mark inactive if canceled in Stripe
        except Exception as e:
            print(f"Error fetching Stripe subscription: {e}")

        return True  # Active otherwise

    def save(self, *args, **kwargs):
        # Ensure start_date is populated (auto_now_add works only on initial save)
        if not self.start_date:
            self.start_date = self.start_date or self._state.adding and date.today()
        
        # Automatically calculate end_date based on the plan's duration
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_in_days)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - (Active: {self.active})"
    



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    video = models.FileField(upload_to='blog_videos/', default='videos/default_video.mp4')
    quote = models.TextField(blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()  # Tag functionality

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Associate comment with a user
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # For approval system
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question