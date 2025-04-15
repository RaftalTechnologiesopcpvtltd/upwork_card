$(document).ready(function () {
  let currentProducts = [];

  function getProductPrice(product) {
    let priceStr =
      product.selling_type === "Auction"
        ? product.current_bid_price
        : product.product_price;

    if (typeof priceStr === "string") {
      priceStr = priceStr.replace(/\$/g, "").replace(/,/g, "").trim();
    }

    const price = parseFloat(priceStr);
    return isNaN(price) ? 0.0 : price;
  }

  function sortProducts(products, sortType) {
    let sorted = [...products]; // clone

    if (sortType === "low_to_high") {
      sorted.sort((a, b) => getProductPrice(a) - getProductPrice(b));
    } else if (sortType === "high_to_low") {
      sorted.sort((a, b) => getProductPrice(b) - getProductPrice(a));
    }

    return sorted;
  }

  function renderProducts(products) {
    let resultsContainer = $(".category-container");
    resultsContainer.empty();

    if (products.length === 0) {
      resultsContainer.html("<p>No products found.</p>");
      return;
    }

    products.forEach((product) => {
      productData[product.id] = product;

      let productHTML = `
            <div class="my-5 openProductModal position-relative" data-product-id="${
              product.id
            }" 
                data-bs-toggle="modal" data-bs-target="#productModal" style="overflow:hidden;">
                
                <div class="ribbon">${product.website_name || "Unknown"}</div> 

                <div style="border-radius: 0; background-color: #EBF4F3; border: none; overflow: hidden;">
                    <div style="display: flex; justify-content: center; height: 230.5px; width: 230.5px; overflow: hidden; padding: 8%; margin-left: 12%;">
                        <img src="${
                          product.product_images[0]
                        }" class="img-fluid" alt="${product.product_title}">
                    </div>
                </div>
                <div class="p-3">
                    <h5 class="mt-4 card-title" style="font-size: 18px; font-weight: 700;">
                        ${product.product_title}
                    </h5>

                    <h6 class="mt-4 card-title ${
                      String(product.selling_type).includes("Auction")
                        ? "auction-box"
                        : "fixed-price-box"
                    }">
                        ${product.selling_type || "Unknown"}
                    </h6>                                       

                    ${
                      String(product.selling_type).includes("Auction")
                        ? `
                        <p class="bid mb-1"><i class="fas fa-gavel me-2"></i> Current Bid Price: $${
                          product.current_bid_price || "N/A"
                        }</p>
                        <p class="bid mb-1"><i class="fas fa-gavel me-2"></i> Current Bid Count: ${
                          product.current_bid_count || "N/A"
                        }</p>
                    `
                        : `
                        <p class="selling_price mb-1">Selling Price: $${
                          product.product_price || "N/A"
                        }</p>
                    `
                    }

                    <p class="date mb-3"><i class="far fa-calendar-alt me-2"></i> ${
                      product.date || "N/A"
                    }</p>
                </div>
            </div>
        `;

      resultsContainer.append(productHTML);
    });
  }
  let productData = {}; // Store all product data globally
  let LocationHTML = `<option value="auburn">Auburn</option>
                            <option value="birmingham">Birmingham</option>
                            `;

  $("#marketplaceFilter").on("change", function () {
    let marketplace = $(this).val();
    let resultsContainer = $("#locationFilter");

    if (marketplace === "craigslist" || marketplace === "all") {
      resultsContainer.html(LocationHTML);
    } else {
      resultsContainer.html(`<option value="">Select Location</option>`);
    }
  });

  $("#searchBtn").on("click", function () {
    let query = $("#searchInput").val().trim();
    let marketplace = $("#marketplaceFilter").val();
    let location = $("#locationFilter").val();

    $.ajax({
      url: "/search/",
      type: "GET",
      data: { query, marketplace, location },
      beforeSend: function () {
        $(".category-container").html(`<div class="prod_loader-container">
                <div class="prod_pulse"></div>
                <div class="prod_loader"></div>
                <div class="prod_loading-text">Fetching your products...</div>
            </div>`);
      },
      success: function (response) {
        currentProducts = response.products;

        if (currentProducts.length > 0) {
          $("#sortContainer").show(); // Show dropdown
          const sortType = $("#sortSelect").val();
          const sortedProducts = sortProducts(currentProducts, sortType);
          renderProducts(sortedProducts);
        } else {
          $("#sortContainer").hide(); // Hide dropdown
          $(".category-container").html("<p>No products found.</p>");
        }
      },
      error: function () {
        $(".category-container").html("<p>Error fetching results.</p>");
      },
    });
  });

  // 🔁 Whenever user changes dropdown, apply sort
  $("#sortSelect").on("change", function () {
    const sortType = $(this).val();
    const sortedProducts = sortProducts(currentProducts, sortType);
    renderProducts(sortedProducts);
  });

  // Clear Filters Button
  $("#clearBtn").on("click", function () {
    $("#searchInput").val("");
    $("#soldFilter").val("");
    $("#locationFilter").val("");
    $("#marketplaceFilter").val("");
    $(".category-container").empty();
    $("#sortContainer").hide(); // Hide dropdown
  });
  // Handle modal opening
  $(document)
    .on("click", ".openProductModal", function () {
      let productId = $(this).data("product-id");
      let data = productData[productId];

      if (!data) {
        console.error("Product data not found for ID:", productId);
        return;
      } else {
        console.log("Product data found for ID:", productId);
        console.log("Product : ", data);
      }

      let carouselInner = $("#productCarousel .carousel-inner");
      let indicators = $("#carouselIndicators");

      carouselInner.empty();
      indicators.empty();

      let images = Array.isArray(data.product_images)
        ? data.product_images
        : data.product_images
        ? data.product_images.split(",")
        : [];

      if (images.length === 0) {
        carouselInner.append(`
                <div class="carousel-item active" style="height: 500px; background: white;">
                    <img src="" class="d-block w-100" alt="No Image Available">
                </div>`);
      } else {
        images.forEach((imgSrc, index) => {
          let activeClass = index === 0 ? "active" : "";

          carouselInner.append(`
                    <div class="carousel-item ${activeClass}" style="height: 500px; background: white;">
                        <img src="${imgSrc.trim()}" class="d-block product-image" alt="Product Image" style="height: 100%; object-fit: contain;">
                    </div>`);

          indicators.append(`
                    <button type="button" data-bs-target="#productCarousel" 
                            data-bs-slide-to="${index}" class="${activeClass}" aria-label="Slide ${
            index + 1
          }"></button>`);
        });

        // Add navigation buttons only if multiple images exist
        $(".carousel-control-prev, .carousel-control-next").remove();
        if (images.length > 1) {
          $("#productCarousel").append(`
                    <button class="carousel-control-prev changing_btn" type="button" 
                            data-bs-target="#productCarousel" data-bs-slide="prev">
                        <i class="lni lni-arrow-left"></i>
                    </button>
                    <button class="carousel-control-next changing_btn" type="button" 
                            data-bs-target="#productCarousel" data-bs-slide="next">
                        <i class="lni lni-arrow-right"></i>
                    </button>`);
        }
      }

      // Remove and re-add navigation buttons if multiple images exist
      $(".carousel-control-prev, .carousel-control-next").remove();
      if (images.length > 1) {
        $("#productCarousel").append(`
        <button class="carousel-control-prev changing_btn" type="button" 
                data-bs-target="#productCarousel" data-bs-slide="prev">
            <i class="lni lni-arrow-left"></i>
        </button>
        <button class="carousel-control-next changing_btn" type="button" 
                data-bs-target="#productCarousel" data-bs-slide="next">
            <i class="lni lni-arrow-right"></i>
        </button>`);
      }

      // Enable Touch Swipe for Mobile Users
      let carouselElement = document.querySelector("#productCarousel");
      let touchStartX = 0;
      let touchEndX = 0;

      carouselElement.addEventListener("touchstart", (e) => {
        touchStartX = e.changedTouches[0].screenX;
      });

      carouselElement.addEventListener("touchend", (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
      });

      function handleSwipe() {
        if (touchEndX < touchStartX) {
          new bootstrap.Carousel(carouselElement).next();
        }
        if (touchEndX > touchStartX) {
          new bootstrap.Carousel(carouselElement).prev();
        }
      }
      let prod_btns = $("#prod_btns");

      // Check if the button already exists
      if (prod_btns.find(`.add-to-fav`).length === 0) {
        let add_to_fav_btn = `<a href="#" data-product-id="${data.id}" class="mb-2 ml-2 btn btn-danger add-to-fav">
                <i class="fa fa-heart" aria-hidden="true"></i>
                </a>`;
        prod_btns.append(add_to_fav_btn);
      }

      // Populate Product Details
      $("#productTitle").text(data.product_title || "No Title Available");
      $("#sellingtype").text(data.selling_type);
      if (data.selling_type.includes("Auction")) {
        $("#biddinginfo").removeClass("d-none");
        $("#sellingtype").removeClass("fixed-price-box");
        $("#sellingtype").addClass("auction-box");
      } else {
        $("#biddinginfo").addClass("d-none");
        $("#sellingtype").removeClass("auction-box");
        $("#sellingtype").addClass("fixed-price-box");
      }
      $("#productTitlebtm").text(data.product_title || "No Title Available");
      if (data.selling_type.includes("Auction")) {
        $("#productPrice").text(
          data.current_bid_price ? `$${data.current_bid_price}` : "N/A"
        );
        $("#productPrice").removeClass("selling_price");
        $("#productPrice").addClass("bid");
      } else {
        $("#productPrice").text(
          data.product_price ? `$${data.product_price}` : "Price Not Available"
        );
        $("#productPrice").addClass("selling_price");
        $("#productPrice").removeClass("bid");
      }
      $("#productAvailability").text(
        data.product_availability_status || "Unknown"
      );
      $("#productStock").text(
        data.product_availability_quantity || "Not Specified"
      );
      $("#productSold").text(data.product_sold_quantity || "Not Specified");
      $("#productDescription").text(
        data.description || "No description available."
      );

      // Auction Info
      $("#auctionId").text(data.auction_id || "N/A");
      $("#currentBid").text(
        data.current_bid_price ? `$${data.current_bid_price}` : "N/A"
      );
      $("#highestBidder").text(data.highest_bidder || "No Bids");
      $("#bidCount").text(data.current_bid_count || "0");

      // Condition Info
      $("#condition").text(data.condition || "N/A");
      let conditionText = `${data.condition || ""} ${
        data.condition_descriptors_list || ""
      } ${data.condition_values || ""} ${
        data.condition_additional_info || ""
      }`.trim();

      $("#conditionInfo").text(conditionText || "No details available");

      // Shipping Info
      $("#shippingInfo").text(data.shipping_cost || "Not Available");
      $("#estArrival").text(data.estimated_arrival || "Unknown");

      // Return Policy
      $("#returnAccepted").text(data.return_terms_returns_accepted || "N/A");
      $("#refundMethod").text(data.return_terms_refund_method || "N/A");
      $("#returnPeriod").text(
        data.return_terms_return_period_value
          ? `${data.return_terms_return_period_value} ${data.return_terms_return_period_unit}`
          : "N/A"
      );

      // Additional Info
      $("#productBrand").text(data.brand || "N/A");
      $("#productCategory").text(data.category || "N/A");

      // Website & Product Links
      if (data.website_url) {
        $("#websiteUrl")
          .attr("href", data.website_url)
          .text(data.website_name || "Website")
          .parent()
          .show();
      } else {
        $("#websiteUrl").parent().hide();
      }

      if (data.product_link) {
        $("#productLink")
          .attr("href", data.product_link)
          .text("View Product")
          .parent()
          .show();
      } else {
        $("#productLink").parent().hide();
      }

      // Show the modal
      $("#productModal").modal("show");
    })
    .catch((error) => console.error("Error fetching product details:", error));
});
