import requests
import json
from typing import List, Dict, Optional
import logging


logger = logging.getLogger(__name__)
def fetch_offerup(keyword: str, next_page_cursor: Optional[str] = None) -> Dict:
    """
    Fetches listings from OfferUp based on the provided keyword and pagination cursor.

    Args:
        keyword (str): The search keyword.
        next_page_cursor (Optional[str]): Cursor for pagination.

    Returns:
        Dict: JSON response from the OfferUp API.
    """
    url = "https://offerup.com/api/graphql"

    headers = {
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Connection": "keep-alive",
        "Origin": "https://offerup.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "accept": "*/*",
        "content-type": "application/json",
        "ou-browser-user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }

    payload = {
        "operationName": "GetModularFeed",
        "variables": {
            "debug": False,
            "searchParams": [
                {"key": "q", "value": keyword},
                {"key": "platform", "value": "web"},
                {"key": "lon", "value": "-97.822"},
                {"key": "lat", "value": "37.751"},
                {"key": "experiment_id", "value": "experimentmodel24"},
                {"key": "page_cursor", "value": next_page_cursor},
                {"key": "limit", "value": "200"},
            ]
        },
        "query": """query GetModularFeed($searchParams: [SearchParam], $debug: Boolean = false) {
        modularFeed(params: $searchParams, debug: $debug) {
        analyticsData {
            requestId
            searchPerformedEventUniqueId
            searchSessionId
            __typename
        }
        categoryInfo {
            categoryId
            isForcedCategory
            __typename
        }
        feedAdditions
        filters {
            ...modularFilterNumericRange
            ...modularFilterSelectionList
            __typename
        }
        legacyFeedOptions {
            ...legacyFeedOptionListSelection
            ...legacyFeedOptionNumericRange
            __typename
        }
        looseTiles {
            ...modularTileBanner
            ...modularTileBingAd
            ...modularTileGoogleDisplayAd
            ...modularTileJob
            ...modularTileEmptyState
            ...modularTileListing
            ...modularTileLocalDisplayAd
            ...modularTileSearchAlert
            ...modularTileSellerAd
            ...modularModuleTileAdsPostXAd
            __typename
        }
        modules {
            ...modularGridModule
            __typename
        }
        pageCursor
        query {
            ...modularQueryInfo
            __typename
        }
        requestTimeMetadata {
            resolverComputationTimeSeconds
            serviceRequestTimeSeconds
            totalResolverTimeSeconds
            __typename
        }
        searchAlert {
            alertId
            alertStatus
            searchAlertCount
            __typename
        }
        personalizationPath
        debugInformation @include(if: $debug) {
            rankedListings {
            listingId
            attributes {
                key
                value
                __typename
            }
            __typename
            }
            lastViewedItems {
            listingId
            attributes {
                key
                value
                __typename
            }
            __typename
            }
            categoryAffinities {
            affinity
            count
            decay
            affinityOwner
            __typename
            }
            rankingStats {
            key
            value
            __typename
            }
            __typename
        }
        __typename
        }
    }

    fragment modularFilterNumericRange on ModularFeedNumericRangeFilter {
        isExpandedHighlight
        lowerBound {
        ...modularFilterNumericRangeBound
        __typename
        }
        shortcutLabel
        shortcutRank
        subTitle
        targetName
        title
        type
        upperBound {
        ...modularFilterNumericRangeBound
        __typename
        }
        __typename
    }

    fragment modularFilterNumericRangeBound on ModularFeedNumericRangeFilterNumericRangeBound {
        label
        limit
        placeholderText
        targetName
        value
        __typename
    }

    fragment modularFilterSelectionList on ModularFeedSelectionListFilter {
        targetName
        title
        subTitle
        shortcutLabel
        shortcutRank
        type
        isExpandedHighlight
        options {
        ...modularFilterSelectionListOption
        __typename
        }
        __typename
    }

    fragment modularFilterSelectionListOption on ModularFeedSelectionListFilterOption {
        isDefault
        isSelected
        label
        subLabel
        value
        __typename
    }

    fragment legacyFeedOptionListSelection on FeedOptionListSelection {
        label
        labelShort
        name
        options {
        default
        label
        labelShort
        selected
        subLabel
        value
        __typename
        }
        position
        queryParam
        type
        __typename
    }

    fragment legacyFeedOptionNumericRange on FeedOptionNumericRange {
        label
        labelShort
        leftQueryParam
        lowerBound
        name
        options {
        currentValue
        label
        textHint
        __typename
        }
        position
        rightQueryParam
        type
        units
        upperBound
        __typename
    }

    fragment modularTileBanner on ModularFeedTileBanner {
        tileId
        tileType
        title
        __typename
    }

    fragment modularTileBingAd on ModularFeedTileBingAd {
        tileId
        bingAd {
        ouAdId
        adExperimentId
        adNetwork
        adRequestId
        adTileType
        adSettings {
            repeatClickRefractoryPeriodMillis
            collapsible
            __typename
        }
        bingClientId
        clickFeedbackUrl
        clickReturnUrl
        contentUrl
        deepLinkEnabled
        experimentDataHash
        image {
            height
            url
            width
            __typename
        }
        impressionFeedbackUrl
        impressionUrls
        viewableImpressionUrls
        installmentInfo {
            amount
            description
            downPayment
            __typename
        }
        itemName
        lowPrice
        price
        searchId
        sellerName
        templateFields {
            key
            value
            __typename
        }
        __typename
        }
        tileType
        __typename
    }

    fragment modularTileGoogleDisplayAd on ModularFeedTileGoogleDisplayAd {
        tileId
        googleDisplayAd {
        ouAdId
        additionalSizes
        adExperimentId
        adHeight
        adNetwork
        adPage
        adRequestId
        adTileType
        adWidth
        adaptive
        channel
        clickFeedbackUrl
        clientId
        contentUrl
        customTargeting {
            key
            values
            __typename
        }
        displayAdType
        errorDrawable {
            actionPath
            listImage {
            height
            url
            width
            __typename
            }
            __typename
        }
        experimentDataHash
        formatIds
        impressionFeedbackUrl
        personalizationProperties {
            key
            values
            __typename
        }
        prebidConfigs {
            key
            values {
            timeout
            tamSlotUUID
            liftoffPlacementIDs
            nimbusPriceMapping
            adPosition
            __typename
            }
            __typename
        }
        renderLocation
        searchId
        searchQuery
        templateId
        __typename
        }
        tileType
        __typename
    }

    fragment modularTileJob on ModularFeedTileJob {
        tileId
        tileType
        job {
        address {
            city
            state
            zipcode
            __typename
        }
        companyName
        datePosted
        image {
            height
            url
            width
            __typename
        }
        industry
        jobId
        jobListingUrl
        jobOwnerId
        pills {
            text
            type
            __typename
        }
        title
        apply {
            method
            value
            __typename
        }
        wageDisplayValue
        provider
        __typename
        }
        __typename
    }

    fragment modularTileEmptyState on ModularFeedTileEmptyState {
        tileId
        tileType
        title
        description
        iconType
        __typename
    }

    fragment modularTileListing on ModularFeedTileListing {
        tileId
        listing {
        ...modularListing
        __typename
        }
        tileType
        __typename
    }

    fragment modularListing on ModularFeedListing {
        listingId
        conditionText
        flags
        image {
        height
        url
        width
        __typename
        }
        isFirmPrice
        locationName
        price
        title
        vehicleMiles
        __typename
    }

    fragment modularTileLocalDisplayAd on ModularFeedTileLocalDisplayAd {
        tileId
        localDisplayAd {
        ouAdId
        adExperimentId
        adNetwork
        adRequestId
        adTileType
        advertiserId
        businessName
        callToAction
        callToActionType
        clickFeedbackUrl
        contentUrl
        experimentDataHash
        headline
        image {
            height
            url
            width
            __typename
        }
        impressionFeedbackUrl
        searchId
        __typename
        }
        tileType
        __typename
    }

    fragment modularTileSearchAlert on ModularFeedTileSearchAlert {
        tileId
        tileType
        title
        __typename
    }

    fragment modularTileSellerAd on ModularFeedTileSellerAd {
        tileId
        listing {
        ...modularListing
        __typename
        }
        sellerAd {
        ouAdId
        adId
        adExperimentId
        adNetwork
        adRequestId
        adTileType
        clickFeedbackUrl
        experimentDataHash
        impressionFeedbackUrl
        searchId
        __typename
        }
        tileType
        __typename
    }

    fragment modularModuleTileAdsPostXAd on ModularFeedTileAdsPostXAd {
        ...modularTileAdsPostXAd
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularTileAdsPostXAd on ModularFeedTileAdsPostXAd {
        tileId
        adsPostXAd {
        ouAdId
        adExperimentId
        adNetwork
        adRequestId
        adTileType
        clickFeedbackUrl
        experimentDataHash
        impressionFeedbackUrl
        searchId
        offer {
            beacons {
            noThanksClick
            close
            __typename
            }
            title
            description
            clickUrl
            image
            pixel
            ctaYes
            ctaNo
            perkswallLabel
            perkswallUrl
            __typename
        }
        __typename
        }
        tileType
        __typename
    }

    fragment modularGridModule on ModularFeedModuleGrid {
        moduleId
        collection
        formFactor
        grid {
        actionPath
        tiles {
            ...modularModuleTileBingAd
            ...modularModuleTileGoogleDisplayAd
            ...modularModuleTileListing
            ...modularModuleTileLocalDisplayAd
            ...modularModuleTileSellerAd
            __typename
        }
        __typename
        }
        moduleType
        rank
        rowIndex
        searchId
        subTitle
        title
        infoActionPath
        feedIndex
        __typename
    }

    fragment modularModuleTileBingAd on ModularFeedTileBingAd {
        ...modularTileBingAd
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularModuleTileGoogleDisplayAd on ModularFeedTileGoogleDisplayAd {
        ...modularTileGoogleDisplayAd
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularModuleTileListing on ModularFeedTileListing {
        ...modularTileListing
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularModuleTileLocalDisplayAd on ModularFeedTileLocalDisplayAd {
        ...modularTileLocalDisplayAd
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularModuleTileSellerAd on ModularFeedTileSellerAd {
        ...modularTileSellerAd
        moduleId
        moduleRank
        moduleType
        __typename
    }

    fragment modularQueryInfo on ModularFeedQueryInfo {
        appliedQuery
        decisionType
        originalQuery
        suggestedQuery
        __typename
    }



    """

    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def parse_listings(data: Dict) -> List[Dict]:
    """
    Parses the OfferUp API response to extract relevant listing information.

    Args:
        data (Dict): JSON response from the OfferUp API.

    Returns:
        List[Dict]: A list of dictionaries containing listing details.
    """
    listings = []
    try:
        tiles = data.get('data', {}).get('modularFeed', {}).get('looseTiles', [])
        for tile in tiles:
            listing = tile.get('listing')
            if listing:
                product = {
                    "Website Name": "OfferUP",
                    "Website URL": "https://offerup.com/",
                    "Product Link": f"https://offerup.com/item/detail/{listing.get('listingId')}",
                    "Product Images": [listing.get('image', {}).get('url')],
                    "Selling Type": "Fixed",
                    "Product Title": listing.get('title'),
                    "Product Price Currency": "$",
                    "Product Price": listing.get('price'),
                    "Description": f"Listed in {listing.get('locationName')}",
                    "Condition": listing.get('conditionText') or "Not Specified",
                    "Shipping Cost": "Local Pickup Only" if 'LOCAL_PICKUP' in listing.get('flags', []) else "-",
                    "Shipping Currency": "$" if 'LOCAL_PICKUP' in listing.get('flags', []) else "-",
                }
                listings.append(product)
    except Exception as e:
        print(f"Error parsing listings: {e}")
    return listings

def get_data(keyword,location):
    """
    Main function to fetch and parse listings from OfferUp.
    """
    all_products = []
    next_page_cursor = None
    for _ in range(5):
        data = fetch_offerup(keyword, next_page_cursor)
        if not data:
            break
        next_page_cursor = data.get('data', {}).get('modularFeed', {}).get('pageCursor')
        products = parse_listings(data)
        all_products.extend(products)
    print(f"Total products fetched: {len(all_products)}")
    return all_products

def lambda_handler(event, context):
    """
    AWS Lambda handler function to scrape 5miles.com based on 'query' and 'location' from the event.

    Example event:
    {
        "query": "laptop",
        "location": "dallas"
    }
    """
    try:
        query = event.get('query', '')
        location = event.get('location', '')

        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "query" parameter'})
            }

        results = get_data(query,location)

        # If it's an error dict, return as error
        if isinstance(results, dict) and "error" in results:
            return {
                'statusCode': 500,
                'body': json.dumps(results)
            }

        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }