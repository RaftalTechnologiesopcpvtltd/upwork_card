import os
import django
import stripe
from django.conf import settings
from django.utils.timezone import now

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MarketPlace.settings')
django.setup()

from landingpage.models import UserSubscription

def check_subscription():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    today = now().date()

    for subscription in UserSubscription.objects.filter(active=True):
        try:
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            if stripe_sub.status in ["canceled", "past_due", "unpaid"] or subscription.end_date <= today:
                subscription.active = False
                subscription.save(update_fields=['active'])
                print(f"Subscription {subscription.id} deactivated")

        except Exception as e:
            print(f"Error checking subscription {subscription.id}: {e}")

if __name__ == "__main__":
    check_subscription()
