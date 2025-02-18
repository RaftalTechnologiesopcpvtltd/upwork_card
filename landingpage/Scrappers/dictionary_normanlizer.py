common_keys = [
    "Website Name", "Website URL", "Product Link", "Product Title", "Product Images", "Product Price",
    "Product Availibility status", "Product Availibility Quantity", "Product Sold Quantity", "Product Remaining Quantity",
    "Description", "Shipping", "Est. Arrival", "Condition","conditionId","conditionDescriptors","condition_values", "condition_additional_info","Brand", "Category", "Updated",
    "auction_id", "bid_count", "certified_seller", "current_bid", "current_bid_currency", "favorited_count",
    "highest_bidder", "listing_id", "integer_id", "is_owner", "listing_type", "lot_string", "slug",
    "starting_price", "starting_price_currency", "is_closed", "user_bid_status", "user_max_bid", "status",
    "returnTerms_returnsAccepted", "returnTerms_refundMethod", "returnTerms_returnShippingCostPayer",
    "returnTerms_returnPeriod_value", "returnTerms_returnPeriod_unit", "paymentMethods"
]

# Ensure all dictionaries have the same structure with None for missing keys
def normalize_data(data):
    return {key: data.get(key, None) for key in common_keys}
