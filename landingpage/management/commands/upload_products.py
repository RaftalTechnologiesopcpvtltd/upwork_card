import csv
import decimal
import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from landingpage.models import Product


class Command(BaseCommand):
    help = 'Uploads products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Check if the file exists
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"File '{csv_file}' not found."))
            return

        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                product_list = []
                
                for row in reader:
                    try:
                        # Debugging: Print row before processing
                        print(f"Processing row: {row}")

                        # Convert product price (remove $ and ,)
                        try:
                            product_price = decimal.Decimal(row['Product Price'].replace('$', '').replace(',', ''))
                        except (decimal.InvalidOperation, ValueError, AttributeError):
                            product_price = None  # Default to None if conversion fails

                        # Convert integer fields safely
                        def safe_int(value, default=0):
                            try:
                                return int(float(value)) if value else default
                            except (ValueError, TypeError):
                                return default

                        product_availability_quantity = safe_int(row['Product Availibility Quantity'])
                        product_sold_quantity = safe_int(row['Product Sold Quantity'])
                        product_remaining_quantity = safe_int(row['Product Remaining Quantity'])
                        bid_count = safe_int(row['bid_count'])
                        favorited_count = safe_int(row['favorited_count'])
                        integer_id = safe_int(row['integer_id'])
                        return_period_value = safe_int(row['returnTerms_returnPeriod_value'])

                        # Convert other decimal fields safely
                        def safe_decimal(value):
                            try:
                                return decimal.Decimal(value.replace('$', '').replace(',', '')) if value else None
                            except (decimal.InvalidOperation, ValueError, AttributeError):
                                return None

                        current_bid = safe_decimal(row['current_bid'])
                        starting_price = safe_decimal(row['starting_price'])
                        user_max_bid = safe_decimal(row['user_max_bid'])

                        # Create Product instance
                        product = Product(
                            website_name=row.get('Website Name', ''),
                            website_url=row.get('Website URL', ''),
                            product_link=row.get('Product Link', ''),
                            product_title=row.get('Product Title', ''),
                            product_images=row.get('Product Images', ''),
                            product_price=product_price,
                            product_availability_status=row.get('Product Availibility status', ''),
                            product_availability_quantity=product_availability_quantity,
                            product_sold_quantity=product_sold_quantity,
                            product_remaining_quantity=product_remaining_quantity,
                            description=row.get('Description', ''),
                            shipping=row.get('Shipping', ''),
                            est_arrival=row.get('Est. Arrival', ''),
                            condition=row.get('Condition', ''),
                            condition_id=row.get('conditionId', ''),
                            condition_descriptors=row.get('conditionDescriptors', ''),
                            condition_values=row.get('condition_values', ''),
                            condition_additional_info=row.get('condition_additional_info', ''),
                            brand=row.get('Brand', ''),
                            category=row.get('Category', ''),
                            updated=row.get('Updated', ''),
                            auction_id=row.get('auction_id', ''),
                            bid_count=bid_count,
                            certified_seller=row.get('certified_seller', ''),
                            current_bid=current_bid,
                            current_bid_currency=row.get('current_bid_currency', ''),
                            favorited_count=favorited_count,
                            highest_bidder=row.get('highest_bidder', ''),
                            listing_id=row.get('listing_id', ''),
                            integer_id=integer_id,
                            is_owner=row.get('is_owner', False),
                            listing_type=row.get('listing_type', ''),
                            lot_string=row.get('lot_string', ''),
                            slug=row.get('slug', ''),
                            starting_price=starting_price,
                            starting_price_currency=row.get('starting_price_currency', ''),
                            is_closed=row.get('is_closed', False),
                            user_bid_status=row.get('user_bid_status', ''),
                            user_max_bid=user_max_bid,
                            status=row.get('status', ''),
                            return_terms_returns_accepted=row.get('returnTerms_returnsAccepted', ''),
                            return_terms_refund_method=row.get('returnTerms_refundMethod', ''),
                            return_terms_return_shipping_cost_payer=row.get('returnTerms_returnShippingCostPayer', ''),
                            return_terms_return_period_value=return_period_value,
                            return_terms_return_period_unit=row.get('returnTerms_returnPeriod_unit', ''),
                            payment_methods=row.get('paymentMethods', ''),
                        )

                        product_list.append(product)

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Skipping row {row}: {e}"))

                # Bulk insert products
                Product.objects.bulk_create(product_list)
                self.stdout.write(self.style.SUCCESS(f"Successfully uploaded {len(product_list)} products from {csv_file}"))

        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Unicode decode error while reading the file: {e}"))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"File not found: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
