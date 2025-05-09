from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),
    
    # Blogs
    # path('blogs/', views.blog_list, name='admin_blogs'),
    # path('blogs/add/', views.blog_add, name='admin_blog_add'),
    # path('blogs/edit/<int:blog_id>/', views.blog_edit, name='admin_blog_edit'),
    # path('blogs/view/<int:blog_id>/', views.blog_view, name='admin_blog_view'),
    # path('blogs/delete/<int:blog_id>/', views.blog_delete, name='admin_blog_delete'),
    
    # # Subscription Plans
    path('subscriptions/', views.subscription_list, name='admin_subscriptions'),
    # path('subscriptions/add/', views.subscription_add, name='admin_subscription_add'),
    path('subscriptions/edit/<int:plan_id>/', views.subscription_edit, name='admin_subscription_edit'),
    # path('subscriptions/delete/<int:plan_id>/', views.subscription_delete, name='admin_subscription_delete'),
    
    # # Sliders
    # path('sliders/', views.slider_list, name='admin_sliders'),
    # path('sliders/add/', views.slider_add, name='admin_slider_add'),
    # path('sliders/edit/<int:slider_id>/', views.slider_edit, name='admin_slider_edit'),
    # path('sliders/delete/<int:slider_id>/', views.slider_delete, name='admin_slider_delete'),
    
    # # FAQs
    # path('faqs/', views.faq_list, name='admin_faqs'),
    # path('faqs/add/', views.faq_add, name='admin_faq_add'),
    # path('faqs/edit/<int:faq_id>/', views.faq_edit, name='admin_faq_edit'),
    # path('faqs/delete/<int:faq_id>/', views.faq_delete, name='admin_faq_delete'),
    
    # # Contact Messages
    # path('contacts/', views.contact_list, name='admin_contacts'),
    # path('contacts/mark-read/<int:contact_id>/', views.contact_mark_read, name='admin_contact_mark_read'),
    # path('contacts/delete/<int:contact_id>/', views.contact_delete, name='admin_contact_delete'),
]