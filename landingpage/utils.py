from datetime import datetime
import decimal
from landingpage.models import Product


def safe_int(value, default=0):
    try:
        return int(float(value)) if value else default
    except (ValueError, TypeError):
        return default


def safe_decimal(value):
    try:
        return decimal.Decimal(str(value).replace("$", "").replace(",", "")) if value else None
    except (decimal.InvalidOperation, ValueError, AttributeError):
        return None


def safe_bool(value):
    return str(value).strip().lower() in ["true", "1", "yes"]


def safe_date(value):
    if not value or value.strip().lower() in ["", "none", "null"]:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None  # Return None if the format is incorrect


def create_product(product_data):
    product = Product.objects.create(
        website_name=product_data.get("Website Name", ""),
        website_url=product_data.get("Website URL", ""),
        product_link=product_data.get("Product Link", ""),
        product_title=product_data.get("Product Title", ""),
        product_images=product_data.get("Product Images", ""),
        selling_type=product_data.get("Selling Type", ""),
        product_price=safe_decimal(product_data.get("Product Price")),
        product_price_currency=product_data.get("Product Price Currency", "USD"),
        current_bid_price=safe_decimal(product_data.get("Current Bid Price")),
        current_bid_currency=product_data.get("Current Bid Currency", "USD"),
        current_bid_count=safe_int(product_data.get("Current Bid Count")),
        description=product_data.get("Description", ""),
        condition=product_data.get("Condition", ""),
        condition_id=product_data.get("Condition Id", ""),
        condition_descriptors=product_data.get("Condition Descriptors", ""),
        condition_values=product_data.get("Condition Values", ""),
        condition_additional_info=product_data.get("Condition Additional Info", ""),
        product_availability_status=product_data.get("Product Availibility status", ""),
        product_availability_quantity=safe_int(product_data.get("Product Availibility Quantity")),
        product_sold_quantity=safe_int(product_data.get("Product Sold Quantity")),
        product_remaining_quantity=safe_int(product_data.get("Product Remaining Quantity")),
        shipping_cost=safe_decimal(product_data.get("Shipping Cost")),
        shipping_currency=product_data.get("Shipping Currency", "USD"),
        shipping_service_code=product_data.get("Shipping Service Code", ""),
        shipping_carrier_code=product_data.get("Shipping Carrier Code", ""),
        shipping_type=product_data.get("Shipping Type", ""),
        additional_shipping_cost_per_unit=safe_decimal(product_data.get("Additional Shipping Cost Per Unit")),
        additional_shipping_cost_currency=product_data.get("Additional Shipping Cost Currency", "USD"),
        shipping_cost_type=product_data.get("Shipping Cost Type", ""),
        estimated_arrival=product_data.get("Estimated Arrival", ""),
        brand=product_data.get("Brand", ""),
        category=product_data.get("Category", ""),
        auction_id=product_data.get("Auction Id", ""),
        bid_count=safe_int(product_data.get("Bid Count")),
        certified_seller=safe_bool(product_data.get("Certified Seller")),
        favorited_count=safe_int(product_data.get("Favorited Count")),
        highest_bidder=product_data.get("Highest Bidder", ""),
        listing_id=product_data.get("Listing Id", ""),
        integer_id=safe_int(product_data.get("Integer Id")),
        is_owner=safe_bool(product_data.get("Is Owner")),
        listing_type=product_data.get("Listing Type", ""),
        lot_string=product_data.get("Lot String", ""),
        slug=product_data.get("Slug", ""),
        starting_price=safe_decimal(product_data.get("Starting Price")),
        starting_price_currency=product_data.get("Starting Price Currency", "USD"),
        is_closed=safe_bool(product_data.get("Is Closed")),
        user_bid_status=product_data.get("User Bid Status", ""),
        user_max_bid=safe_decimal(product_data.get("User Max Bid")),
        status=product_data.get("Status", ""),
        return_terms_returns_accepted=safe_bool(product_data.get("ReturnTerms returns Accepted")),
        return_terms_refund_method=product_data.get("ReturnTerms refund Method", ""),
        return_terms_return_shipping_cost_payer=product_data.get("ReturnTerms return Shipping Cost Payer", ""),
        return_terms_return_period_value=safe_int(product_data.get("ReturnTerms return Period Value")),
        return_terms_return_period_unit=product_data.get("ReturnTerms return Period Unit", ""),
        payment_methods=product_data.get("Payment Methods", ""),
        quantity_used_for_estimate=safe_int(product_data.get("Quantity Used For Estimate")),
        min_estimated_delivery_date=safe_date(product_data.get("Min Estimated Delivery Date")),
        max_estimated_delivery_date=safe_date(product_data.get("Max Estimated Delivery Date")),
        buying_options=product_data.get("Buying Options", ""),
        minimum_price_to_bid=safe_decimal(product_data.get("Minimum Price to Bid")),
        minimum_price_currency=product_data.get("Minimum Price Currency", "USD"),
        unique_bidder_count=safe_int(product_data.get("Unique Bidder Count")),
    )
    return product