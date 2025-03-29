import csv
import decimal
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from landingpage.models import Product

class Command(BaseCommand):
    help = "Uploads products from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"File '{csv_file}' not found."))
            return

        try:
            with open(csv_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                product_list = []

                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value else default
                    except (ValueError, TypeError):
                        return default

                def safe_decimal(value):
                    try:
                        return decimal.Decimal(value.replace("$", "").replace(",", "")) if value else None
                    except (decimal.InvalidOperation, ValueError, AttributeError):
                        return None

                def safe_bool(value):
                    return str(value).strip().lower() in ["true", "1", "yes"]

                def safe_date(value):
                    if not value or value.strip() in ["", "None", "null"]:
                        return None
                    try:
                        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
                    except ValueError:
                        return None  # Return None if the format is incorrect

                for row in reader:
                    try:
                        product = Product(
                            website_name=row.get("Website Name"),
                            website_url=row.get("Website URL"),
                            product_link=row.get("Product Link"),
                            product_title=row.get("Product Title"),
                            product_images=row.get("Product Images"),
                            selling_type = row.get("Selling Type"),
                            product_price=safe_decimal(row.get("Product Price")),
                            product_price_currency=row.get("Product Price Currency"),
                            current_bid_price=safe_decimal(row.get("Current Bid Price")),
                            current_bid_currency=row.get("Current Bid Currency", "USD"),
                            current_bid_count=safe_int(row.get("Current Bid Count")),
                            description=row.get("Description"),
                            condition=row.get("Condition"),
                            condition_id=row.get("Condition Id"),
                            condition_descriptors=row.get("Condition Descriptors"),
                            condition_values=row.get("Condition Values"),
                            condition_additional_info=row.get("Condition Additional Info"),
                            product_availability_status=row.get("Product Availability Status"),
                            product_availability_quantity=safe_int(row.get("Product Availability Quantity")),
                            product_sold_quantity=safe_int(row.get("Product Sold Quantity")),
                            product_remaining_quantity=safe_int(row.get("Product Remaining Quantity")),
                            shipping_cost=safe_decimal(row.get("Shipping Cost")),
                            shipping_currency=row.get("Shipping Currency", "USD"),
                            shipping_service_code=row.get("Shipping Service Code"),
                            shipping_carrier_code=row.get("Shipping Carrier Code"),
                            shipping_type=row.get("Shipping Type"),
                            additional_shipping_cost_per_unit=safe_decimal(row.get("Additional Shipping Cost Per Unit")),
                            additional_shipping_cost_currency=row.get("Additional Shipping Cost Currency", "USD"),
                            shipping_cost_type=row.get("Shipping Cost Type"),
                            estimated_arrival=row.get("Estimated Arrival"),
                            brand=row.get("Brand"),
                            category=row.get("Category"),
                            auction_id=row.get("Auction Id"),
                            bid_count=safe_int(row.get("Bid Count")),
                            certified_seller=safe_bool(row.get("Certified Seller")),
                            favorited_count=safe_int(row.get("Favorited Count")),
                            highest_bidder=row.get("Highest Bidder"),
                            listing_id=row.get("Listing Id"),
                            integer_id=safe_int(row.get("Integer Id")),
                            is_owner=safe_bool(row.get("Is Owner")),
                            listing_type=row.get("Listing Type"),
                            lot_string=row.get("Lot String"),
                            slug=row.get("Slug"),
                            starting_price=safe_decimal(row.get("Starting Price")),
                            starting_price_currency=row.get("Starting Price Currency", "USD"),
                            is_closed=safe_bool(row.get("Is Closed")),
                            user_bid_status=row.get("User Bid Status"),
                            user_max_bid=safe_decimal(row.get("User Max Bid")),
                            status=row.get("Status"),
                            return_terms_returns_accepted=safe_bool(row.get("Return Terms Returns Accepted")),
                            return_terms_refund_method=row.get("Return Terms Refund Method"),
                            return_terms_return_shipping_cost_payer=row.get("Return Terms Return Shipping Cost Payer"),
                            return_terms_return_period_value=safe_int(row.get("Return Terms Return Period Value")),
                            return_terms_return_period_unit=row.get("Return Terms Return Period Unit"),
                            payment_methods=row.get("Payment Methods"),
                            quantity_used_for_estimate=safe_int(row.get("Quantity Used For Estimate")),
                            min_estimated_delivery_date=safe_date(row.get("Min Estimated Delivery Date")),
                            max_estimated_delivery_date=safe_date(row.get("Max Estimated Delivery Date")),
                            buying_options=row.get("Buying Options"),
                            minimum_price_to_bid=safe_decimal(row.get("Minimum Price to Bid")),
                            minimum_price_currency=row.get("Minimum Price Currency", "USD"),
                            unique_bidder_count=safe_int(row.get("Unique Bidder Count")),
                        )

                        product_list.append(product)

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Skipping row {row}: {e}"))

                if product_list:
                    Product.objects.bulk_create(product_list)
                    self.stdout.write(self.style.SUCCESS(f"Successfully uploaded {len(product_list)} products from {csv_file}"))
                else:
                    self.stdout.write(self.style.WARNING("No valid products found to upload."))

        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Unicode decode error while reading the file: {e}"))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"File not found: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
