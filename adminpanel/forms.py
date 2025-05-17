from django import forms
from landingpage.models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserForm(forms.ModelForm):
    username = forms.CharField(required=False)  # Explicitly add the username field

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=False,
        label='Password'
    )
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'gender',
            'city', 'country', 'address', 'zip_code', 'country_code','username'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
            'country_code': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        # `editing` tells us if this is an edit operation
        self.editing = kwargs.pop('editing', False)
        super().__init__(*args, **kwargs)

        if self.editing:
            # If editing an existing user, hide the password field
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['password'].required = False

    def clean_username(self):
        # Use email as username fallback
        return self.cleaned_data.get('username') or self.cleaned_data.get('email')

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        elif not self.editing:
            raise forms.ValidationError("Password is required.")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # or username fallback logic
        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'video', 'quote', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'postTitle',
                'placeholder': 'Enter post title',
                'required': True
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input',
                'id': 'postImage',
                'accept': 'image/*',
                'required': False
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input',
                'id': 'postVideo',
                'accept': 'video/*',
                'required': False  # Set to True if you want video to be mandatory
            }),
            'quote': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'postQuote',
                'rows': 2,
                'placeholder': 'Enter a memorable quote for your post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'postContent',
                'rows': 6,
                'placeholder': 'Write your blog post content here',
                'required': True
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'postTags',
                'placeholder': 'Enter tags separated by commas'
            }),
        }
        labels = {
            'title': 'Title',
            'image': 'Image',
            'quote': 'Quote',
            'content': 'Content',
            'tags': 'Tags'
        }
        help_texts = {
            'tags': 'Example: technology, coding, web development'
        }
        


class UserSubscriptionForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = [
            'user', 'plan', 'active', 'subscription_id', 'customer_id',
            'session_id', 'payment_status', 'interval', 'start_date', 'end_date'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'subscription_id': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_id': forms.TextInput(attrs={'class': 'form-control'}),
            'session_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_status': forms.TextInput(attrs={'class': 'form-control'}),
            'interval': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class SliderForm(forms.ModelForm):
    class Meta:
        model = Slidder
        fields = ['heading', 'image', 'text', 'order', 'is_active']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Ensure order is set correctly if not explicitly set
        if instance.order is None or instance.order <= 0:
            max_order = Slidder.objects.aggregate(models.Max('order'))['order__max'] or 0
            instance.order = max_order + 1  # Auto-increment order if it's not provided

        if commit:
            instance.save()

            # Reorder all sliders after saving
            Slidder.reorder_all()

        return instance

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = [
            'price_heading',
            'product_id',
            'price',
            'price_id',
            'desc',
            'duration_in_days',
            'price_feature1',
            'price_feature2',
            'price_feature3',
            'price_feature4',
        ]
        widgets = {
            'price_heading': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan Name'}),
            'product_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Id'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'price_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price Id'}),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'duration_in_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration (in days)'}),
            'price_feature1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature 1'}),
            'price_feature2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature 2'}),
            'price_feature3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature 3'}),
            'price_feature4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature 4'}),
        }

class ContactusForm(forms.ModelForm):
    class Meta:
        model = Contactus
        fields = '__all__'
        widgets = {
            'company_about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
        }