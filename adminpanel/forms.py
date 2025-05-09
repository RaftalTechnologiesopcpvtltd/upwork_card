from django import forms
from landingpage.models import *

# class BlogForm(forms.ModelForm):
#     tags = forms.CharField(required=False, widget=forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Enter tags separated by commas'
#     }))
    
#     class Meta:
#         model = BlogPost
#         fields = ['title', 'slug', 'content', 'excerpt', 'category', 
#                   'featured_image', 'is_published', 'is_featured']
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'slug': forms.TextInput(attrs={'class': 'form-control'}),
#             'content': forms.Textarea(attrs={'class': 'form-control summernote'}),
#             'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
#             'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

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