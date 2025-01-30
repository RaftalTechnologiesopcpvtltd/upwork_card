from django.urls import path
from . import views

urlpatterns = [
    path('', views.Landing_page, name='landingpage'),  # Default route for the landing page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('subscribe/<int:plan_id>/', views.subscribe_to_plan, name='subscribe_to_plan'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('my-dashboard/', views.dashboard_view, name='dashboard_view'),
    path('create/', views.create_post, name='create_post'),
    path('blog_listings/', views.blog_listings, name='blog_listings'),
    path('blog_post/<int:post_id>/', views.blog_post, name='blog_post'),
    path('faq/', views.faq, name='faq'),
]
