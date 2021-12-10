$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************
  const ERROR_MESSAGES = {
    USER_ID_WRONG_TYPE: "User ID should be an integer.",
    WISHLIST_ID: "Wishlist ID should be defined as an integer.",
    USER_ID_WISHLIST_NAME_MISSING: "User ID and name should be defined.",
    WISHLIST_NAME_MISSING: "Wishlist name cannot be empty.",
    PRODUCT_NAME_MISSING: "Wishlist name cannot be empty.",
    MISSING_PRODUCT_FIELDS: "Inventory ID, product name, product price and wishlist ID should be defined.",
    PRODUCT_FIELDS_WRONG_TYPE: "Inventory ID, product price and wishlist ID should be integers.",
    PRODUCT_ID_WISHLIST_ID: "Product ID and Wishlist ID should be defined as integers.",
    PRODUCT_IID_AND_PRICE: "Inventory ID and Price should be defined as Integer and Float respectively.",
  };

  // Updates the form with data from the response
  function update_wishlist_form_data(res) {
    $("#wishlist-id").val(res.id);
    $("#wishlist-name").val(res.name);
    $("#wishlist-user-id").val(res.user_id);
  }

  function update_product_form_data(res) {
    $("#wishlist-product-id").val(res.id);
    $("#wishlist-inventory-product-id").val(res.inventory_product_id);
    $("#wishlist-product-name").val(res.name);
    $("#wishlist-product-price").val(res.price);
    $("#wishlist-product-status").val(res.status);
    $("#wishlist-product-pic").val(res.pic_url);
    $("#wishlist-product-description").val(res.short_desc);
  }

  // Creates the results section for each wishlist
  function add_wishlist_row(record, parent) {
    const wishlist_id = record.id || '';
    const name = record.name || '';
    const user_id = record.user_id || '';
    let wishlist_block = $("<div>", {"class": "wishlist-block", "id": `wishlist-block-${wishlist_id}`},);
    wishlist_block.append(`<div class="wishlist-block__name">${name}</div>
    <div class="d-inline">(#<div class="wishlist-block__id">${wishlist_id}</div>)</div>
    <div>By user <div class="wishlist-block__user-id">${user_id}</div></div>`
    );
    if (!record.products) {
      parent.append(wishlist_block);
      return;
    }

    let products_list = $("<div>", {"class": "wishlist-block__products"});
    for (item of record.products) {
      const { id, inventory_product_id, name, pic_url='', price, short_desc='', status, in_cart_status } = item;
      console.log(item)
      let product_list_item = $("<div>", {"class": "wishlist-block__products-item", "id": `products-item-${id}`});

      if (pic_url)
        product_list_item.append(`<div class="products-item__image"><img class="img-thumbnail" src=${pic_url} /></div>`);

        product_list_item.append(`<div>
          <div class="products-item__name">${name}</div>
          ${short_desc ? `<div class="products-item__desc">${short_desc}</div>` : ''}
          <div>$<div class="products-item__price">${price}</div></div>
          <div class="products-item__status">${status.toLowerCase()}</div>
          <div>#<div class="products-item__id">${id}</div>, sku <div class="products-item__inv-id">${inventory_product_id}</div></div>
          ${in_cart_status != 'DEFAULT' ? "<div class=\"products-item__in-cart\">This product is in the shopping cart.</div>" : ''}
          <div class="d-none products-item__wishlist-id">${wishlist_id}</div>
        </div>`);

      products_list.append(product_list_item);
    }

    if (record.products.length == 0) {
      wishlist_block.append('<div>Wishlist is empty.</div>')
    } else {
      wishlist_block.append(products_list);
    }
    parent.append(wishlist_block);
  }

  function build_wishlist_results_table(data) {
    $("#search-results").empty();
    let results_block = $("<div>");

    if (Array.isArray(data)) {
      for (let i=0; i<data.length; i++)
        add_wishlist_row(data[i], results_block);
    } else {
      add_wishlist_row(data, results_block);
    }

    $("#search-results").append(results_block);
  }

  function add_product_row(data, results_table) {
    const {
      id,
      inventory_product_id,
      name,
      pic_url='',
      price,
      short_desc='',
      status,
      wishlist_id,
      in_cart_status
    } = data;

    let row = "<tr><td class=\"results-product-table__product-id col-md-2\">"+id+"</td>"
      +"<td class=\"results-product-table__name col-md-2\">"+name+"</td>"
      +"<td class=\"results-product-table__price col-md-2\">"+price+"</td>"
      +"<td class=\"results-tproduct-able__inv-id col-md-2\">"+inventory_product_id +"</td>"
      +"<td class=\"results-product-table__wishlist-id col-md-2\">"+wishlist_id +"</td>"
      +"<td class=\"results-product-table__status col-md-2\">"+status+"</td>"

    if (short_desc) row += "<td class=\"results-product-table__desc col-md-2\">"+short_desc +"</td>"
    if (pic_url) row += "<td class=\"results-product-table__image col-md-2\"><a href=\""+pic_url +"\">pic</a></td>"

    row += "</tr>";
    results_table.append(row);
  }

  function build_product_results_table(data) {
    $("#search-results").empty();
    let results_table = $("<table>", {"class": "table-striped", "cellpadding": "10"});
    let header = $('<tr>');
    header.append('<th class="col-md-2">ID</th>');
    header.append('<th class="col-md-2">Name</th>');
    header.append('<th class="col-md-2">Price</th>');
    header.append('<th class="col-md-2">Inventory \#</th></tr>');
    header.append('<th class="col-md-2">Wishlist ID</th></tr>');
    header.append('<th class="col-md-2">Status</th></tr>');
    header.append('<th class="col-md-2">Description</th></tr>');
    header.append('<th class="col-md-2">Picture</th></tr>');

    results_table.append(header);
    add_product_row(data, results_table);
    $("#search-results").append(results_table);
  }

  // Clears the results table
  function clear_table() {
    $("#search-results").empty();
  }

  // Clears all form fields
  function clear_form_data() {
    $("#wishlist-name").val("");
    $("#wishlist-user-id").val("");
    $("#wishlist-product-id").val("");
    $("#wishlist-inventory-product-id").val("");
    $("#wishlist-product-name").val("");
    $("#wishlist-product-price").val("");
    $("#wishlist-product-status").val(1);
    $("#wishlist-product-pic").val("");
    $("#wishlist-product-description").val("");
  }

  // Updates the flash message area
  function flash_message(message) {
    $("#flash-message").empty();
    $("#flash-message").text(message);
  }

  // ****************************************
  // Create a Wishlist
  // ****************************************
  $("#create-wishlist").click(function (event) {
    event.preventDefault();
    clear_table();

    var name = $("#wishlist-name").val();
    var user_id = $("#wishlist-user-id").val();

    if (!name || !user_id) {
      flash_message(ERROR_MESSAGES.USER_ID_WISHLIST_NAME_MISSING)
      return;
    }

    if (isNaN(parseInt(user_id))) {
      flash_message(ERROR_MESSAGES.USER_ID_WRONG_TYPE)
      return;
    }

    var data = {
      "name": name,
      "user_id": parseInt(user_id),
    };

    var ajax = $.ajax({
        type: "POST",
        url: "/wishlists",
        contentType:"application/json",
        data: JSON.stringify(data),
    });

    ajax.done(function(res){
      // update_wishlist_form_data(res["data"]);
      build_wishlist_results_table(res);
      flash_message("Wishlist Created!");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

  // ****************************************
  // Clear the form
  // ****************************************
  $("#wishlists-clear").click(function () {
    $("#wishlist-id").val("");
    clear_form_data();
  });

  // ****************************************
  // Search for a Wishlist
  // ****************************************

  $("#search-wishlist").click(function (event) {
    event.preventDefault();
    clear_table();

    const user_id = $("#wishlist-user-id").val();
    const wishlist_id = $("#wishlist-id").val();
    let queryString = "";

    if (wishlist_id && isNaN(parseInt(wishlist_id))) {
      flash_message(ERROR_MESSAGES.WISHLIST_ID);
      return;
    }

    if (user_id && isNaN(parseInt(user_id))) {
      flash_message(ERROR_MESSAGES.USER_ID_WRONG_TYPE);
      return;
    }

    if (user_id) {
      queryString += "?user_id=" + parseInt(user_id);
    }

    const url = wishlist_id ? `/wishlists/${parseInt(wishlist_id)}` : `/wishlists`+ queryString;
    var ajax = $.ajax({
      type: "GET",
      url,
    });

    ajax.done(function(res){
      build_wishlist_results_table(res);
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

  // ****************************************
  // Update a Wishlist
  // ****************************************

  $("#rename-wishlist").click(function (event) {
    event.preventDefault();
    clear_table();

    var name = $("#wishlist-name").val();
    var id = parseInt($("#wishlist-id").val());

    if (isNaN(id)) {
      flash_message(ERROR_MESSAGES.WISHLIST_ID);
      return;
    }

    if (name === "") {
      flash_message(ERROR_MESSAGES.WISHLIST_NAME_MISSING);
      return;
    }

    var data = {
      "name": name,
    };

    var ajax = $.ajax({
      type: "PUT",
      url: `/wishlists/`+ id,
      contentType: "application/json",
      data: JSON.stringify(data)
    });

    ajax.done(function(res){
      // update_wishlist_form_data(res["data"]);
      build_wishlist_results_table(res);
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });

  });

  // ****************************************
  // Delete a Wishlist
  // ****************************************

  $("#delete-wishlist").click(function (event) {
    event.preventDefault();
    clear_table();

    var wishlist_id = parseInt($("#wishlist-id").val());

    if (isNaN(wishlist_id)) {
      flash_message(ERROR_MESSAGES.WISHLIST_ID);
      return;
    }

    var ajax = $.ajax({
      type: "DELETE",
      url: `/wishlists/` + wishlist_id,
      contentType: "application/json",
      data: '',
    })

    ajax.done(function(res){
      clear_form_data();
      flash_message("Wishlist Deleted!");
    });

    ajax.fail(function(res){
      flash_message("Server error!");
      clear_table();
    });
  });

  // ****************************************
  // Add a product to a Wishlist
  // ****************************************
  $("#add-product").click(function (event) {
    event.preventDefault();
    clear_table();

    const inventory_product_id_value = $("#wishlist-inventory-product-id").val();
    const product_name = $("#wishlist-product-name").val();
    const product_price_value = $("#wishlist-product-price").val();
    const product_status = $("#wishlist-product-status").val();
    const product_pic = $("#wishlist-product-pic").val();
    const product_description = $("#wishlist-product-description").val();
    const wishlist_id = parseInt($('#wishlist-id').val());

    if (!inventory_product_id_value || !product_name || !product_price_value) {
      flash_message(ERROR_MESSAGES.MISSING_PRODUCT_FIELDS);
      return;
    }

    const inventory_product_id = parseInt(inventory_product_id_value);
    const product_price = parseFloat(product_price_value);

    if (isNaN(inventory_product_id) || isNaN(product_price) || isNaN(wishlist_id)) {
      flash_message(ERROR_MESSAGES.PRODUCT_FIELDS_WRONG_TYPE);
      return;
    }

    const data = {
      "name": product_name,
      "price": product_price,
      "status": parseInt(product_status),
      "pic_url": product_pic,
      "short_desc": product_description,
      "inventory_product_id": inventory_product_id,
      "wishlist_id":  wishlist_id
    };

    var ajax = $.ajax({
      type: "POST",
      url: `/wishlists/${wishlist_id}/products`,
      contentType: "application/json",
      data: JSON.stringify(data),
    });

    ajax.done(function(){
      flash_message("Product was added to wishlist.");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

  // ****************************************
  // Get a product in a Wishlist
  // ****************************************
  $("#search-product").click(function (event) {
    event.preventDefault();
    clear_table();

    const product_id = parseInt($('#wishlist-product-id').val());
    const wishlist_id = parseInt($('#wishlist-id').val());

    if (isNaN(product_id) || isNaN(wishlist_id)) {
      flash_message("Product ID and Wishlist ID should be defined as integers.")
      return;
    }

    var ajax = $.ajax({
      type: "GET",
      url: `/wishlists/${wishlist_id}/products/${product_id}`,
      contentType: "application/json",
      data: '',
    });

    ajax.done(function(res){
      flash_message("Success");
      build_product_results_table(res);
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

  // ****************************************
  // Delete a Product
  // ****************************************

  $("#delete-product").click(function (event) {
    event.preventDefault();
    clear_table();

    const product_id = parseInt($("#wishlist-product-id").val());
    const wishlist_id = parseInt($("#wishlist-id").val());

    if (isNaN(product_id) || isNaN(wishlist_id)) {
      flash_message(ERROR_MESSAGES.PRODUCT_ID_WISHLIST_ID);
      return;
    }

    var ajax = $.ajax({
      type: "DELETE",
      url: `/wishlists/` + wishlist_id + `/products/` + product_id,
      contentType: "application/json",
      data: '',
    })

    ajax.done(function(res){
      clear_form_data();
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

  // ****************************************
  // Update a Product
  // ****************************************
  $("#update-product").click(function (event) {
    event.preventDefault();
    clear_table();

    const wishlist_id = parseInt($("#wishlist-id").val());
    const name = $("#wishlist-product-name").val();
    const product_id = parseInt($("#wishlist-product-id").val());
    const i_id = $("#wishlist-inventory-product-id").val();
    const price = $("#wishlist-product-price").val();
    const status = $("#wishlist-product-status").val();
    const pic = $("#wishlist-product-pic").val();
    const desc = $("#wishlist-product-description").val();
    console.log(wishlist_id, product_id)

    if (isNaN(wishlist_id) || isNaN(product_id)) {
      flash_message(ERROR_MESSAGES.PRODUCT_ID_WISHLIST_ID);
      return;
    }

    if ((i_id && isNaN(parseInt(i_id))) || (price && isNaN(parseFloat(price)))) {
      flash_message(ERROR_MESSAGES.PRODUCT_IID_AND_PRICE);
      return;
    }

    const data = {
      status: parseInt(status),
      ...name && { name },
      ...i_id && { inventory_product_id: parseInt(i_id) },
      ...price && { price: parseFloat(price) },
      ...pic && {pic_url: pic},
      ...desc && { short_desc: desc }
    };

    var ajax = $.ajax({
      type: "PUT",
      url: `/wishlists/${wishlist_id}/products/${product_id}`,
      contentType: "application/json",
      data: JSON.stringify(data)
    });

    ajax.done(function(res){
      build_product_results_table(res);
      flash_message("Updated Success!");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
    });
  });

  // #####################################################################
  // PLACE A PRODUCT IN A WISHLIST TO CART
  // #####################################################################
  $("#order-product").click(function (event) {
    event.preventDefault();
    clear_table();

    const product_id = parseInt($('#wishlist-product-id').val());
    const wishlist_id = parseInt($('#wishlist-id').val());

    if (isNaN(product_id) || isNaN(wishlist_id)) {
      flash_message(ERROR_MESSAGES.PRODUCT_ID_WISHLIST_ID);
      return;
    }

    var ajax = $.ajax({
      type: "PUT",
      url: `/wishlists/${wishlist_id}/products/${product_id}/add-to-cart`,
      contentType: "application/json",
      data: '',
    })

    ajax.done(function(){
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });

});
