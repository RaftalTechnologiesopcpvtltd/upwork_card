from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

    
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(required=False)  # Explicitly add the username field

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'gender','phone_number', 'country_code','password1', 'password2', 'username')
        widgets = {
             'gender': forms.Select(attrs={'class': 'form-control','placeholder':'Select your Gender'}),
             'country_code': forms.Select(attrs={'class': 'form-control','placeholder':'Select your Country'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Add a placeholder option to gender field
        self.fields['gender'].choices = [('', 'Select your Gender')] + list(self.fields['gender'].choices)

        # Add a placeholder option to country_code field
        self.fields['country_code'].choices = [('', '+00')] + list(self.fields['country_code'].choices)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        # Use first_name as username if username is not provided
        return self.cleaned_data.get('username') or self.cleaned_data.get('email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Ensure username is set to first_name
        if commit:
            user.save()
        return user
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        labels = {'body': ''}  # This removes the label instead of using None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].widget.attrs.update({
            'class': 'form-control mb-4',
            'placeholder': 'Write your comment...'
        })



from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'quote', 'content', 'tags']
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
