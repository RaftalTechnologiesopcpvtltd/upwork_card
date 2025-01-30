from django.contrib import admin
from .models import *

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name','gender','address','city','country','zip_code')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name','gender','address','city','country','zip_code')

class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name','gender','is_staff','address','city','country','zip_code']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender','address','city','country','zip_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'category', 'gender','password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions','address','city','country','zip_code'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 'category')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)




admin.site.register(Slidder)
admin.site.register(Contactus)
admin.site.register(Pricing)
admin.site.register(UserSubscription)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "Approve selected comments"

admin.site.register(Comment, CommentAdmin)

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'tags')

admin.site.register(BlogPost, BlogPostAdmin)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')