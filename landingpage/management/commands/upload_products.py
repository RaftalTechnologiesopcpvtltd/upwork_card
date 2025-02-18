import csv
from django.core.management.base import BaseCommand
from landingpage.models import Product

import decimal
from django.core.exceptions import ValidationError



class Command(BaseCommand):
    help = 'Uploads products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Preprocess product price to remove dollar sign and commas
                    try:
                        product_price = row['Product Price'].replace('$', '').replace(',', '')
                        product_price = decimal.Decimal(product_price) if product_price else None
                    except (decimal.InvalidOperation, ValueError):
                        product_price = None  # Handle invalid price
                    
                    # Handle product availability quantity
                    try:
                        product_availability_quantity = int(row['Product Availibility Quantity']) if row['Product Availibility Quantity'] else 0
                    except (ValueError, TypeError):
                        product_availability_quantity = 0  # Handle invalid or empty availability quantity
                    
                    # Handle product sold quantity
                    try:
                        product_sold_quantity = int(row['Product Sold Quantity']) if row['Product Sold Quantity'] else 0
                    except (ValueError, TypeError):
                        product_sold_quantity = 0  # Handle invalid or empty sold quantity

                    # Handle product remaining quantity
                    try:
                        product_remaining_quantity = int(row['Product Remaining Quantity']) if row['Product Remaining Quantity'] else 0
                    except (ValueError, TypeError):
                        product_remaining_quantity = 0  # Handle invalid or empty remaining quantity

                    # Ensure other fields are valid and prepare Product object
                    product = Product(
                        website_name=row['Website Name'] or '',
                        website_url=row['Website URL'] or '',
                        product_link=row['Product Link'] or '',
                        product_title=row['Product Title'] or '',
                        product_images=row['Product Images'] or '',  # Adjust this if needed
                        product_price=product_price,
                        product_availability_status=row['Product Availibility status'] or '',
                        product_availability_quantity=product_availability_quantity,
                        product_sold_quantity=product_sold_quantity,
                        product_remaining_quantity=product_remaining_quantity,
                        description=row['Description'] or '',
                        shipping=row['Shipping'] or '',
                        est_arrival=row['Est. Arrival'] or '',
                        condition=row['Condition'] or '',
                        condition_id=row['conditionId'] or '',
                        condition_descriptors=row['conditionDescriptors'] or '',
                        condition_values=row['condition_values'] or '',
                        condition_additional_info=row['condition_additional_info'] or '',
                        brand=row['Brand'] or '',
                        category=row['Category'] or '',
                        updated=row['Updated'] or '',
                        auction_id=row['auction_id'] or '',
                        bid_count=int(row['bid_count']) if row['bid_count'] else 0,
                        certified_seller=row['certified_seller'] or '',
                        current_bid=decimal.Decimal(row['current_bid'].replace('$', '').replace(',', '')) if row['current_bid'] else None,
                        current_bid_currency=row['current_bid_currency'] or '',
                        favorited_count=int(row['favorited_count']) if row['favorited_count'] else 0,
                        highest_bidder=row['highest_bidder'] or '',
                        listing_id=row['listing_id'] or '',
                        integer_id=int(row['integer_id']) if row['integer_id'] else 0,
                        is_owner=row['is_owner'] or False,
                        listing_type=row['listing_type'] or '',
                        lot_string=row['lot_string'] or '',
                        slug=row['slug'] or '',
                        starting_price=decimal.Decimal(row['starting_price'].replace('$', '').replace(',', '')) if row['starting_price'] else None,
                        starting_price_currency=row['starting_price_currency'] or '',
                        is_closed=row['is_closed'] or False,
                        user_bid_status=row['user_bid_status'] or '',
                        user_max_bid=decimal.Decimal(row['user_max_bid'].replace('$', '').replace(',', '')) if row['user_max_bid'] else None,
                        status=row['status'] or '',
                        return_terms_returns_accepted=row['returnTerms_returnsAccepted'] or '',
                        return_terms_refund_method=row['returnTerms_refundMethod'] or '',
                        return_terms_return_shipping_cost_payer=row['returnTerms_returnShippingCostPayer'] or '',
                        return_terms_return_period_value=int(row['returnTerms_returnPeriod_value']) if row['returnTerms_returnPeriod_value'] else 0,
                        return_terms_return_period_unit=row['returnTerms_returnPeriod_unit'] or '',
                        payment_methods=row['paymentMethods'] or '',
                    )

                    # Save the product to the database
                    try:
                        product.save()
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f"Error saving product: {e.message}"))
                        continue

        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Unicode decode error while reading the file: {e}"))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"File not found: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded products from {csv_file}'))