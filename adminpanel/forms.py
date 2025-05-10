from django import forms
from landingpage.models import *


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'gender',
            'city', 'country', 'address', 'zip_code', 'country_code'
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
                'required': True
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

# class SliderForm(forms.ModelForm):
#     class Meta:
#         model = Slidder
#         fields = ['title', 'subtitle', 'image', 'button_text', 
#                   'button_url', 'order', 'is_active']
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#             'button_text': forms.TextInput(attrs={'class': 'form-control'}),
#             'button_url': forms.URLInput(attrs={'class': 'form-control'}),
#             'order': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class FAQForm(forms.ModelForm):
#     class Meta:
#         model = FAQ
#         fields = ['question', 'answer', 'category', 'order', 'is_active']
#         widgets = {
#             'question': forms.TextInput(attrs={'class': 'form-control'}),
#             'answer': forms.Textarea(attrs={'class': 'form-control summernote'}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'order': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }