from django.urls import path
from . import views

urlpatterns = [
    path('', views.Landing_page, name='landingpage'),  # Default route for the landing page
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('subscribe/<int:plan_id>/', views.subscribe_to_plan, name='subscribe_to_plan'),
    # path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('my-dashboard/', views.dashboard_view, name='dashboard_view'),
    path('my-profile/', views.profile, name='profile'),
    path('create/', views.create_post, name='create_post'),
    path('blog_listings/', views.blog_listings, name='blog_listings'),
    path('blog_post/<int:post_id>/', views.blog_post, name='blog_post'),
    path('faq/', views.faq, name='faq'),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
    path("cancel-subscription/", views.cancel_subscription, name="cancel_subscription"),
    path("resume-subscription/", views.resume_subscription, name="resume_subscription"),
    path("update-subscription/", views.update_subscription, name="update_subscription"),
    path("check-unpaid-invoices/", views.check_unpaid_invoices, name="check_unpaid_invoices"),
    path("process-refund/", views.process_refund, name="process_refund"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("search/", views.product_search, name="product_search"),
    path('get-product/<int:product_id>/', views.get_product_details, name='get_product_details'),
    path('bulk-upload/', views.bulk_upload_products, name='bulk_upload_products'),
]