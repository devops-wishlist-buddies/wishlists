$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

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

  // Creates the results table
  function add_row(record, results_table) {
    const id = record.id || '';
    const name = record.name || '';
    const user_id = record.user_id || ''
    const product_list = JSON.stringify(record.products) || ''
    const row = "<tr><td class=\"results-table__wishlist-id col-md-2\">"+id+"</td><td class=\"col-md-4\">"+name+
      "</td><td class=\"col-md-2\">"+user_id+"</td><td class=\"col-md-6\">"+product_list +"</td></tr>";
    results_table.append(row);
  }

  function build_table(data) {
    $("#search-results").empty();
    let results_table = $("<table>", {"class": "table-striped", "cellpadding": "10"});
    let header = $('<tr>');
    header.append('<th class="col-md-2">ID</th>');
    header.append('<th class="col-md-4">Name</th>');
    header.append('<th class="col-md-2">User_ID</th>');
    header.append('<th class="col-md-6">Products</th></tr>');
    results_table.append(header);
    if (Array.isArray(data)) {
      for (let i = 0; i < data.length; i++) {
        add_row(data[i], results_table);
      }
    } else {
      add_row(data, results_table);
    }

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
    var name = $("#wishlist-name").val();
    var user_id = $("#wishlist-user-id").val();

    if (!name || !user_id) {
      flash_message("User id and name should be defined")
      return;
    }

    var data = {
      "name": name,
      "user_id": Number(user_id),
    };

    var ajax = $.ajax({
        type: "POST",
        url: `/wishlists`,
        contentType:"application/json",
        data: JSON.stringify(data),
    });

    ajax.done(function(res){
      // update_wishlist_form_data(res["data"]);
      build_table(res["data"]);
      flash_message(res["message"]);
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
    const user_id = $("#wishlist-user-id").val();
    const wishlist_id = $("#wishlist-id").val();
    let queryString = "?";

    if (user_id) {
      queryString += "user_id=" + user_id;
    }

    const url = wishlist_id ? `/wishlists/${wishlist_id}` : `/wishlists`+ queryString;
    var ajax = $.ajax({
      type: "GET",
      url,
      contentType: "application/json",
      data: ''
    });

    ajax.done(function(res){
      build_table(res['data']);
      update_wishlist_form_data(res['data'][0]);
      update_product_form_data(res['data'][0].products[0]);
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
    var name = $("#wishlist-name").val();
    var id = $("#wishlist-id").val();

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
      build_table(res["data"]);
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
    var wishlist_id = $("#wishlist-id").val();

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

    inventory_product_id = $("#wishlist-inventory-product-id").val();
    product_name = $("#wishlist-product-name").val();
    product_price = $("#wishlist-product-price").val();
    product_status = $("#wishlist-product-status").val();
    product_pic = $("#wishlist-product-pic").val();
    product_description = $("#wishlist-product-description").val();
    wishlist_id = $('#wishlist-id').val();

    if (!inventory_product_id || !product_name || !product_price || !wishlist_id) {
      flash_message('Inventory ID, product name, product price and wishlist id should be defined')
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
    }

    var ajax = $.ajax({
      type: "POST",
      url: `/wishlists/${wishlist_id}/products`,
      contentType: "application/json",
      data: JSON.stringify(data),
    })

    ajax.done(function(){
      flash_message("Product was added to wishlist.");
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
    var product_id = $("#wishlist-product-id").val();

    var ajax = $.ajax({
      type: "DELETE",
      url: `/wishlists/products/` + parseInt(product_id),
      contentType: "application/json",
      data: '',
    })

    ajax.done(function(res){
      clear_form_data();
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message("Product doesn't exist!");
      clear_table();
    });
  });

  // ****************************************
  // Update a Product
  // ****************************************

  $("#update-product").click(function (event) {
    event.preventDefault();
    var name = $("#wishlist-product-name").val();
    var id = $("#wishlist-product-id").val();
    var i_id = $("#wishlist-inventory-product-id").val();
    var price = $("#wishlist-product-price").val();
    var status = $("#wishlist-product-status").val();
    var pic = $("#wishlist-product-pic").val();
    var desc = $("#wishlist-product-description").val();

    var data = {};

    if(name){
      data.name = name;
    }
    if(i_id){
      data.inventory_product_id = parseInt(i_id);
    }
    if(price){
      data.price = parseFloat(price);
    }
    if(status){
      if(status == "AVAILABLE"){
        data.status = 1;
      }else{
        data.status = 0;
      }
    }
    if(pic){
      data.pic_url = pic;
    }
    if(desc){
      data.short_desc = desc;
    }

    if(!data){
      flash_message("Nothing Updated!");
      return;
    }

    var ajax = $.ajax({
      type: "PUT",
      url: `/wishlists/products/`+ id,
      contentType: "application/json",
      data: JSON.stringify(data)
    });

    ajax.done(function(res){
      update_product_form_data(res["data"]);
      flash_message("Updated Success!");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
    });

  });

// ****************************************
  // Search for a Product
  // ****************************************

  $("#search-product").click(function (event) {
    event.preventDefault();
    const id = $("#wishlist-product-id").val();

    var ajax = $.ajax({
      type: "GET",
      url: `/wishlists/products/` + id,
      contentType: "application/json",
      data: ''
    });

    ajax.done(function(res){
      update_product_form_data(res['data']);
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
      clear_table();
    });
  });
});
