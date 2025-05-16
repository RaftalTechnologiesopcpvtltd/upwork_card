from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),

    # User
    path('users/', views.user_list, name='admin_users'),
    path('users/add/', views.user_add, name='admin_user_add'),
    path('users/edit/<int:user_id>/', views.user_edit, name='admin_user_edit'),
    # path('users/view/<int:user_id>/', views.user_view, name='admin_user_view'),
    path('users/delete/<int:user_id>/', views.user_delete, name='admin_user_delete'),

    #search_history
    path('admin_search_history/', views.search_history, name='admin_search_history'),


    # Blogs
    path('blogs/', views.blog_list, name='admin_blogs'),
    path('blogs/add/', views.blog_add, name='admin_blog_add'),
    path('blogs/edit/<int:blog_id>/', views.blog_edit, name='admin_blog_edit'),
    path('blogs/comments/<int:post_id>/', views.blog_comment_list, name='blog_comment_list'),
    path('blogs/comment/approve/<int:comment_id>/', views.approve_comment, name='approve_comment'),
    path('blogs/view/<int:blog_id>/', views.blog_view, name='admin_blog_view'),
    path('blogs/delete/<int:blog_id>/', views.blog_delete, name='admin_blog_delete'),
    

    # Pricing
    path('pricings/', views.pricing_list, name='pricing'),
    path('pricings/add/', views.pricing_add, name='admin_pricing_add'),
    path('pricings/edit/<int:pricing_id>/', views.pricing_edit, name='admin_pricing_edit'),
    path('pricings/edit/status/<int:pricing_id>/', views.pricing_status, name='admin_pricing_edit_status'),
    path('pricings/delete/<int:pricing_id>/', views.pricing_delete, name='admin_pricing_delete'),
    
    # # Subscription Plans
    path('subscriptions/', views.subscription_list, name='admin_subscriptions'),
    # path('subscriptions/add/', views.subscription_add, name='admin_subscription_add'),
    path('subscriptions/edit/<int:plan_id>/', views.subscription_edit, name='admin_subscription_edit'),
    path('subscriptions/cancel/', views.subscription_cancel, name='admin_subscription_cancel'),
    
    # # Sliders
    path('sliders/', views.slider_list, name='admin_sliders'),
    path('sliders/add/', views.slider_add, name='admin_slider_add'),
    path('sliders/edit/<int:slider_id>/', views.slider_edit, name='admin_slider_edit'),
    path('sliders/delete/<int:slider_id>/', views.slider_delete, name='admin_slider_delete'),
    
    # # FAQs
    path('faqs/', views.faq_list, name='admin_faqs'),
    path('faqs/add/', views.faq_add, name='admin_faq_add'),
    path('faqs/edit/<int:faq_id>/', views.faq_edit, name='admin_faq_edit'),
    path('faqs/delete/<int:faq_id>/', views.faq_delete, name='admin_faq_delete'),
    
    # # Contact Messages
    path('contacts/', views.contact_list, name='admin_contacts'),
    path('contacts/mark-read/<int:contact_id>/', views.contact_mark_read, name='admin_contact_mark_read'),
    path('contacts/delete/<int:contact_id>/', views.contact_delete, name='admin_contact_delete'),
    
    # # Contact Messages
    path('contacts_links/', views.contactus_list, name='contactus_list'),
    path('contacts_links/add/', views.contactus_create, name='contactus_add'),
    path('contacts_links/update/<int:pk>/', views.contactus_update, name='contactus_update'),
    path('contacts_links/delete/<int:pk>/', views.contactus_delete, name='contactus_delete'),
]