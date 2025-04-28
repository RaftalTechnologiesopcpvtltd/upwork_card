$(document).ready(function () {
  let currentProducts = [];

  function getProductPrice(product) {
      let priceStr = product.selling_type === "Auction"
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

      products.forEach(product => {
          productData[product.id] = product;

          let productHTML = 
      <div class="my-5 openProductModal position-relative" data-product-id="${product.id}" 
          data-bs-toggle="modal" data-bs-target="#productModal" style="overflow:hidden;">
          
          <div class="ribbon">${product.website_name || "Unknown"}</div> 

          <div style="border-radius: 0; background-color: #EBF4F3; border: none; overflow: hidden;">
              <div style="display: flex; justify-content: center; height: 230.5px; width: 230.5px; overflow: hidden; padding: 8%; margin-left: 12%;">
                  <img src="${product.product_images[0]}" class="img-fluid" alt="${product.product_title}">
              </div>
          </div>
          <div class="p-3">
              <h5 class="mt-4 card-title" style="font-size: 18px; font-weight: 700;">
                  ${product.product_title}
              </h5>

              <h6 class="mt-4 card-title ${String(product.selling_type).includes('Auction') ? 'auction-box' : 'fixed-price-box'}">
                  ${product.selling_type || "Unknown"}
              </h6>                                       

              ${String(product.selling_type).includes('Auction') ? 
                  <p class="bid mb-1"><i class="fas fa-gavel me-2"></i> Current Bid Price: $${product.current_bid_price || "N/A"}</p>
                  <p class="bid mb-1"><i class="fas fa-gavel me-2"></i> Current Bid Count: ${product.current_bid_count || "N/A"}</p>
               : 
                  <p class="selling_price mb-1">Selling Price: $${product.product_price || "N/A"}</p>
              }

              <p class="date mb-3"><i class="far fa-calendar-alt me-2"></i> ${product.date || "N/A"}</p>
          </div>
      </div>
  ;

          resultsContainer.append(productHTML);
      });
  }
  let productData = {}; // Store all product data globally
  let LocationHTML = `<option value="auburn">Auburn</option>
                      <option value="birmingham">Birmingham</option>
                      <option value="dothan">Dothan</option>
                      <option value="florence / muscle shoals">Florence / muscle shoals</option>
                      <option value="gadsden-anniston">Gadsden-anniston</option>
                      <option value="huntsville / decatur">Huntsville / decatur</option>
                      <option value="mobile">Mobile</option>
                      <option value="montgomery">Montgomery</option>
                      <option value="tuscaloosa">Tuscaloosa</option>
                      <option value="anchorage / mat-su">Anchorage / mat-su</option>
                      <option value="fairbanks">Fairbanks</option>
                      <option value="kenai peninsula">Kenai peninsula</option>
                      <option value="southeast alaska">Southeast alaska</option>
                      <option value="flagstaff / sedona">Flagstaff / sedona</option>
                      <option value="mohave county">Mohave county</option>
                      <option value="phoenix">Phoenix</option>
                      <option value="prescott">Prescott</option>
                      <option value="show low">Show low</option>
                      <option value="sierra vista">Sierra vista</option>
                      <option value="tucson">Tucson</option>
                      <option value="yuma">Yuma</option>
                      <option value="fayetteville">Fayetteville</option>
                      <option value="fort smith">Fort smith</option>
                      <option value="jonesboro">Jonesboro</option>
                      <option value="little rock">Little rock</option>
                      <option value="texarkana">Texarkana</option>
                      <option value="bakersfield">Bakersfield</option>
                      <option value="chico">Chico</option>
                      <option value="fresno / madera">Fresno / madera</option>
                      <option value="gold country">Gold country</option>
                      <option value="hanford-corcoran">Hanford-corcoran</option>
                      <option value="humboldt county">Humboldt county</option>
                      <option value="imperial county">Imperial county</option>
                      <option value="inland empire">Inland empire</option>
                      <option value="los angeles">Los angeles</option>`
                      ;

  $("#marketplaceFilter").on("change", function () {
      let marketplace = $(this).val();
      let resultsContainer = $("#locationFilter");

      if (marketplace === 'Craigslist' || marketplace === 'ALL') {
          resultsContainer.html(LocationHTML);
      } else {
          resultsContainer.html(<option value="">Select Location</option>);
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
              $(".category-container").html(<div class="prod_loader-container">
          <div class="prod_pulse"></div>
          <div class="prod_loader"></div>
          <div class="prod_loading-text">Fetching your products...</div>
      </div>);
          },
          success: function (response) {
              allFetchedProducts = response.products; // Store all fetched products
              currentProducts = [...allFetchedProducts]; // Initially set current products to all fetched

              if (currentProducts.length > 0) {
                  $("#sortContainer").show();  // Show dropdown
                  const sortType = $("#sortSelect").val();
                  const sortedProducts = sortProducts(currentProducts, sortType);
                  renderProducts(sortedProducts);

                  // After successful search, update marketplace filter to act as a filter
                  $("#marketplaceFilter").off("change"); // Remove initial change handler
                  $("#marketplaceFilter").on("change", function () {
                      let selectedMarketplace = $(this).val();
                      console.log("selectedMarketplaceSuccess : ", selectedMarketplace);

                      if (selectedMarketplace === 'Fivemiles') {
                          selectedMarketplace = "miles";
                      }

                      console.log("selectedMarketplaceSuccess : ", selectedMarketplace);

                      let filteredProducts;
                      if (selectedMarketplace === 'ALL') {
                          filteredProducts = [...allFetchedProducts];
                      } else {
                          filteredProducts = allFetchedProducts.filter(product => product.website_name && product.website_name.toLowerCase().includes(selectedMarketplace.toLowerCase()));
                      }
                      currentProducts = filteredProducts;
                      const sortType = $("#sortSelect").val();
                      const sortedProducts = sortProducts(currentProducts, sortType);
                      renderProducts(sortedProducts);
                      if (currentProducts.length > 0) {
                          $("#sortContainer").show();
                      } else {
                          $("#sortContainer").hide();
                          $(".category-container").html("<p>No products found for this marketplace.</p>");
                      }
                  });

              } else {
                  $("#sortContainer").hide();  // Hide dropdown
                  $(".category-container").html("<p>No products found.</p>");
              }
          },
          error: function () {
              $(".category-container").html("<p>Error fetching results.</p>");
          }
      });
  });

  // 🔁 Whenever user changes sort dropdown, apply sort
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
      $("#sortContainer").hide();  // Hide dropdown

      // Reset marketplace filter functionality to its initial state
      $("#marketplaceFilter").off("change");
      $("#marketplaceFilter").on("change", function () {
          let marketplace = $(this).val();
          let resultsContainer = $("#locationFilter");
          console.log("selectedMarketplace : ", selectedMarketplace);
          console.log("marketplace : ", marketplace);

          if (marketplace === 'Craigslist' || marketplace === 'ALL') {
              resultsContainer.html(LocationHTML);
          } else {
              resultsContainer.html('<option value="">Select Location</option>');
          }
          if (allFetchedProducts.length > 0) {
              currentProducts = [...allFetchedProducts];
              if (marketplace !== 'ALL') {
                  currentProducts = currentProducts.filter(product => product.website_name && product.website_name.toLowerCase().includes(selectedMarketplace.toLowerCase()));
              }
              const sortType = $("#sortSelect").val();
              const sortedProducts = sortProducts(currentProducts, sortType);
              renderProducts(sortedProducts);
              if (currentProducts.length > 0) {
                  $("#sortContainer").show();
              } else {
                  $("#sortContainer").hide();
                  $(".category-container").html("<p>No products found for this marketplace.</p>");
              }
          }
      });
      currentProducts = [];
      allFetchedProducts = [];
  });