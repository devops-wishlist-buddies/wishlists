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
      update_wishlist_form_data(res["data"]);
      flash_message(res["message"]);
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
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
    console.log(event)
    const user_id = $("#wishlist-user-id").val();
    const wishlist_id = $("#wishlist-id").val();
    let queryString = "?";

    if (user_id) {
      queryString += "user_id=" + user_id;
    }

    const url = wishlist_id ? `/wishlists/${wishlist_id}` : `/wishlists`+ queryString;
    console.log(url)
    var ajax = $.ajax({
      type: "GET",
      url,
      contentType: "application/json",
      data: ''
    });

    ajax.done(function(res){
      $("#search-results").empty();
      $("#search-results").append('<table class="table-striped" cellpadding="10">');
      var header = '<tr>';
      header += '<th style="width:10%">ID</th>';
      header += '<th style="width:30%">Name</th>';
      header += '<th style="width:10%">User_ID</th>';
      header += '<th style="width:50%">Products</th></tr>';
      $("#search-results").append(header);
      var firstWishlist = "";
      res = res["data"];
      if (wishlist_id) {
        var row = "<tr><td class=\"results-table__wishlist-id\">"+res.id+"</td><td>"+res.name+"</td><td>"+res.user_id+
          "</td><td>"+JSON.stringify(res.products)+"</td></tr>";
        $("#search-results").append(row);
      }
      else {
        for(var i = 0; i < res.length; i++) {
          var wishlist = res[i];
          var row = "<tr><td class=\"results-table__wishlist-id\">"+wishlist.id+"</td><td>"+wishlist.name+"</td><td>"+wishlist.user_id+
            "</td><td>"+JSON.stringify(wishlist.products)+"</td></tr>";
          $("#search-results").append(row);
          if (i == 0) {
            firstWishlist = wishlist;
            }
        }
      }

      $("#search-results").append('</table>');
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
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
      update_wishlist_form_data(res["data"]);
      flash_message("Success");
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message);
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
    });
  });

});
