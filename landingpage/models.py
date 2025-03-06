from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from datetime import timedelta
from datetime import date
from taggit.managers import TaggableManager  # Import taggit
import stripe
from django.utils import timezone
from django.conf import settings


from django.db import models

class Product(models.Model):
    website_name = models.CharField(max_length=255, null=True)
    website_url = models.URLField(null=True)
    product_link = models.URLField(null=True)
    product_title = models.CharField(max_length=255, null=True)
    product_images = models.TextField(null=True)  # Store image URLs as a comma-separated string
    product_price_currency = models.CharField(max_length=10, null=True)
    selling_type =   models.CharField(max_length=10, null=True,  default="")
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    current_bid_currency = models.CharField(max_length=10, null=True, default="USD")
    current_bid_count = models.IntegerField(null=True, default=0)
    description = models.TextField(null=True)
    
    condition = models.CharField(max_length=255, null=True)
    condition_id = models.CharField(max_length=100, null=True)
    condition_descriptors = models.TextField(null=True)  
    condition_values = models.TextField(null=True)  
    condition_additional_info = models.TextField(null=True)
    
    product_availability_status = models.CharField(max_length=100, null=True)
    product_availability_quantity = models.IntegerField(null=True, default=0)
    product_sold_quantity = models.IntegerField(null=True, default=0)
    product_remaining_quantity = models.IntegerField(null=True, default=0)
    
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    shipping_currency = models.CharField(max_length=10, null=True, default="USD")
    shipping_service_code = models.CharField(max_length=100, null=True)
    shipping_carrier_code = models.CharField(max_length=100, null=True)
    shipping_type = models.CharField(max_length=100, null=True)
    additional_shipping_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    additional_shipping_cost_currency = models.CharField(max_length=10, null=True, default="USD")
    shipping_cost_type = models.CharField(max_length=100, null=True)
    
    estimated_arrival = models.CharField(max_length=255, null=True)
    brand = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    
    updated = models.DateTimeField(auto_now=True)  # Automatically updates on save
    auction_id = models.CharField(max_length=100, null=True)
    bid_count = models.IntegerField(null=True, default=0)
    certified_seller = models.BooleanField(null=True, default=False)
    favorited_count = models.IntegerField(null=True, default=0)
    highest_bidder = models.CharField(max_length=255, null=True)
    listing_id = models.CharField(max_length=100, null=True)
    integer_id = models.IntegerField(null=True)
    is_owner = models.BooleanField(null=True, default=False)
    listing_type = models.CharField(max_length=100, null=True)
    lot_string = models.CharField(max_length=100, null=True)
    slug = models.SlugField(null=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    starting_price_currency = models.CharField(max_length=10, null=True, default="USD")
    is_closed = models.BooleanField(null=True, default=False)
    
    user_bid_status = models.CharField(max_length=100, null=True)
    user_max_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    status = models.CharField(max_length=100, null=True)
    
    return_terms_returns_accepted = models.BooleanField(null=True, default=False)
    return_terms_refund_method = models.CharField(max_length=100, null=True)
    return_terms_return_shipping_cost_payer = models.CharField(max_length=100, null=True)
    return_terms_return_period_value = models.IntegerField(null=True, default=0)
    return_terms_return_period_unit = models.CharField(max_length=50, null=True)
    
    payment_methods = models.TextField(null=True)  
    quantity_used_for_estimate = models.IntegerField(null=True, default=1)
    min_estimated_delivery_date = models.DateField(null=True)
    max_estimated_delivery_date = models.DateField(null=True)
    buying_options = models.TextField(null=True)  
    minimum_price_to_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    minimum_price_currency = models.CharField(max_length=10, null=True, default="USD")
    unique_bidder_count = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.product_title

class Favourites(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.product.product_title}'


class MyListing(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # website_name = models.CharField(max_length=255, null=True)
    # website_url = models.URLField(null=True)
    # product_link = models.URLField(null=True)
    product_title = models.CharField(max_length=255, null=True)
    # product_images = models.TextField(null=True)  # Store image URLs as a comma-separated string
    # product_price_currency = models.CharField(max_length=10, null=True)
    # selling_type =   models.CharField(max_length=10, null=True,  default="")
    # product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # current_bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # current_bid_currency = models.CharField(max_length=10, null=True, default="USD")
    # current_bid_count = models.IntegerField(null=True, default=0)
    # description = models.TextField(null=True)
    
    # condition = models.CharField(max_length=255, null=True)
    # condition_id = models.CharField(max_length=100, null=True)
    # condition_descriptors = models.TextField(null=True)  
    # condition_values = models.TextField(null=True)  
    # condition_additional_info = models.TextField(null=True)
    
    # product_availability_status = models.CharField(max_length=100, null=True)
    # product_availability_quantity = models.IntegerField(null=True, default=0)
    # product_sold_quantity = models.IntegerField(null=True, default=0)
    # product_remaining_quantity = models.IntegerField(null=True, default=0)
    
    # shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # shipping_currency = models.CharField(max_length=10, null=True, default="USD")
    # shipping_service_code = models.CharField(max_length=100, null=True)
    # shipping_carrier_code = models.CharField(max_length=100, null=True)
    # shipping_type = models.CharField(max_length=100, null=True)
    # additional_shipping_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # additional_shipping_cost_currency = models.CharField(max_length=10, null=True, default="USD")
    # shipping_cost_type = models.CharField(max_length=100, null=True)
    
    # estimated_arrival = models.CharField(max_length=255, null=True)
    # brand = models.CharField(max_length=255, null=True)
    # category = models.CharField(max_length=255, null=True)
    
    # updated = models.DateTimeField(auto_now=True)  # Automatically updates on save
    # auction_id = models.CharField(max_length=100, null=True)
    # bid_count = models.IntegerField(null=True, default=0)
    # certified_seller = models.BooleanField(null=True, default=False)
    # favorited_count = models.IntegerField(null=True, default=0)
    # highest_bidder = models.CharField(max_length=255, null=True)
    # listing_id = models.CharField(max_length=100, null=True)
    # integer_id = models.IntegerField(null=True)
    # is_owner = models.BooleanField(null=True, default=False)
    # listing_type = models.CharField(max_length=100, null=True)
    # lot_string = models.CharField(max_length=100, null=True)
    # slug = models.SlugField(null=True)
    # starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # starting_price_currency = models.CharField(max_length=10, null=True, default="USD")
    # is_closed = models.BooleanField(null=True, default=False)
    
    # user_bid_status = models.CharField(max_length=100, null=True)
    # user_max_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # status = models.CharField(max_length=100, null=True)
    
    # return_terms_returns_accepted = models.BooleanField(null=True, default=False)
    # return_terms_refund_method = models.CharField(max_length=100, null=True)
    # return_terms_return_shipping_cost_payer = models.CharField(max_length=100, null=True)
    # return_terms_return_period_value = models.IntegerField(null=True, default=0)
    # return_terms_return_period_unit = models.CharField(max_length=50, null=True)
    
    # payment_methods = models.TextField(null=True)  
    # quantity_used_for_estimate = models.IntegerField(null=True, default=1)
    # min_estimated_delivery_date = models.DateField(null=True)
    # max_estimated_delivery_date = models.DateField(null=True)
    # buying_options = models.TextField(null=True)  
    # minimum_price_to_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    # minimum_price_currency = models.CharField(max_length=10, null=True, default="USD")
    # unique_bidder_count = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.product_title
    

class CustomUser(AbstractUser):
    GENDER_CHOICES =(
        ('male','Male'),
        ('female','Female'),
    ('prefer not to say','Prefer Not to Say'),
    )
    COUNTRY_CODE_CHOICES = (
        ('+1', '+1 (US/Canada)'),
        ('+91', '+91 (India)'),
        ('+86', '+86 (China)'),
        ('+81', '+81 (Japan)'),
        ('+49', '+49 (Germany)'),
        ('+33', '+33 (France)'),
        ('+39', '+39 (Italy)'),
        ('+34', '+34 (Spain)'),
        ('+55', '+55 (Brazil)'),
        ('+52', '+52 (Mexico)'),
        ('+7', '+7 (Russia)'),
        ('+27', '+27 (South Africa)'),
        ('+234', '+234 (Nigeria)'),
        ('+254', '+254 (Kenya)'),
        ('+54', '+54 (Argentina)'),
        ('+57', '+57 (Colombia)'),
        ('+65', '+65 (Singapore)'),
        ('+64', '+64 (New Zealand)'),
        ('+353', '+353 (Ireland)'),
        ('+46', '+46 (Sweden)'),
        ('+47', '+47 (Norway)'),
        ('+358', '+358 (Finland)'),
        ('+45', '+45 (Denmark)'),
        ('+48', '+48 (Poland)'),
        ('+351', '+351 (Portugal)'),
        ('+30', '+30 (Greece)'),
        ('+90', '+90 (Turkey)'),
        ('+971', '+971 (United Arab Emirates)'),
        ('+966', '+966 (Saudi Arabia)'),
        ('+972', '+972 (Israel)'),
        ('+852', '+852 (Hong Kong)'),
        ('+886', '+886 (Taiwan)'),
        ('+63', '+63 (Philippines)'),
        ('+66', '+66 (Thailand)'),
        ('+60', '+60 (Malaysia)'),
        ('+84', '+84 (Vietnam)'),
        ('+92', '+92 (Pakistan)'),
        ('+93', '+93 (Afghanistan)'),
        ('+94', '+94 (Sri Lanka)'),
        ('+95', '+95 (Myanmar)'),
        ('+98', '+98 (Iran)'),
        ('+212', '+212 (Morocco)'),
        ('+213', '+213 (Algeria)'),
        ('+216', '+216 (Tunisia)'),
        ('+218', '+218 (Libya)'),
        ('+220', '+220 (Gambia)'),
        ('+221', '+221 (Senegal)'),
        ('+222', '+222 (Mauritania)'),
        ('+223', '+223 (Mali)'),
        ('+224', '+224 (Guinea)'),
        ('+225', '+225 (Ivory Coast)'),
        ('+226', '+226 (Burkina Faso)'),
        ('+227', '+227 (Niger)'),
        ('+228', '+228 (Togo)'),
        ('+229', '+229 (Benin)'),
        ('+230', '+230 (Mauritius)'),
        ('+231', '+231 (Liberia)'),
        ('+232', '+232 (Sierra Leone)'),
        ('+233', '+233 (Ghana)'),
        ('+234', '+234 (Nigeria)'),
        ('+235', '+235 (Chad)'),
        ('+236', '+236 (Central African Republic)'),
        ('+237', '+237 (Cameroon)'),
        ('+238', '+238 (Cape Verde)'),
        ('+239', '+239 (São Tomé and Príncipe)'),
        ('+240', '+240 (Equatorial Guinea)'),
        ('+241', '+241 (Gabon)'),
        ('+242', '+242 (Congo)'),
        ('+243', '+243 (Democratic Republic of the Congo)'),
        ('+244', '+244 (Angola)'),
        ('+245', '+245 (Guinea-Bissau)'),
        ('+246', '+246 (British Indian Ocean Territory)'),
        ('+248', '+248 (Seychelles)'),
        ('+250', '+250 (Rwanda)'),
        ('+251', '+251 (Ethiopia)'),
        ('+252', '+252 (Somalia)'),
        ('+253', '+253 (Djibouti)'),
        ('+254', '+254 (Kenya)'),
        ('+255', '+255 (Tanzania)'),
        ('+256', '+256 (Uganda)'),
        ('+257', '+257 (Burundi)'),
        ('+258', '+258 (Mozambique)'),
        ('+260', '+260 (Zambia)'),
        ('+261', '+261 (Madagascar)'),
        ('+262', '+262 (Réunion)'),
        ('+263', '+263 (Zimbabwe)'),
        ('+264', '+264 (Namibia)'),
        ('+265', '+265 (Malawi)'),
        ('+266', '+266 (Lesotho)'),
        ('+267', '+267 (Botswana)'),
        ('+268', '+268 (Eswatini)'),
        ('+269', '+269 (Comoros)'),
        ('+290', '+290 (Saint Helena)'),
        ('+291', '+291 (Eritrea)'),
        ('+297', '+297 (Aruba)'),
        ('+298', '+298 (Faroe Islands)'),
        ('+299', '+299 (Greenland)'),
        ('+350', '+350 (Gibraltar)'),
        ('+351', '+351 (Portugal)'),
        ('+352', '+352 (Luxembourg)'),
        ('+353', '+353 (Ireland)'),
        ('+354', '+354 (Iceland)'),
        ('+355', '+355 (Albania)'),
        ('+356', '+356 (Malta)'),
        ('+357', '+357 (Cyprus)'),
        ('+358', '+358 (Finland)'),
        ('+359', '+359 (Bulgaria)'),
        ('+370', '+370 (Lithuania)'),
        ('+371', '+371 (Latvia)'),
        ('+372', '+372 (Estonia)'),
        ('+373', '+373 (Moldova)'),
        ('+374', '+374 (Armenia)'),
        ('+375', '+375 (Belarus)'),
        ('+376', '+376 (Andorra)'),
        ('+377', '+377 (Monaco)'),
        ('+378', '+378 (San Marino)'),
        ('+379', '+379 (Vatican City)'),
        ('+380', '+380 (Ukraine)'),
        ('+381', '+381 (Serbia)'),
        ('+382', '+382 (Montenegro)'),
        ('+383', '+383 (Kosovo)'),
        ('+385', '+385 (Croatia)'),
        ('+386', '+386 (Slovenia)'),
        ('+387', '+387 (Bosnia and Herzegovina)'),
        ('+389', '+389 (North Macedonia)'),
        ('+420', '+420 (Czech Republic)'),
        ('+421', '+421 (Slovakia)'),
        ('+423', '+423 (Liechtenstein)'),
        ('+500', '+500 (Falkland Islands)'),
        ('+501', '+501 (Belize)'),
        ('+502', '+502 (Guatemala)'),
        ('+503', '+503 (El Salvador)'),
        ('+504', '+504 (Honduras)'),
        ('+505', '+505 (Nicaragua)'),
        ('+506', '+506 (Costa Rica)'),
        ('+507', '+507 (Panama)'),
        ('+508', '+508 (Saint Pierre and Miquelon)'),
        ('+509', '+509 (Haiti)'),
        ('+590', '+590 (Guadeloupe)'),
        ('+591', '+591 (Bolivia)'),
        ('+592', '+592 (Guyana)'),
        ('+593', '+593 (Ecuador)'),
        ('+594', '+594 (French Guiana)'),
        ('+595', '+595 (Paraguay)'),
        ('+596', '+596 (Martinique)'),
        ('+597', '+597 (Suriname)'),
        ('+598', '+598 (Uruguay)'),
        ('+599', '+599 (Netherlands Antilles)'),
    )
    phone_number = models.CharField(max_length=15, blank=True)
    country_code = models.CharField(max_length=5, choices=COUNTRY_CODE_CHOICES, blank=True)
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