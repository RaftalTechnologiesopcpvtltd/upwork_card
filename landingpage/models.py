from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from datetime import timedelta
from datetime import date
from taggit.managers import TaggableManager  # Import taggit



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
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    receipt = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=20, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

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