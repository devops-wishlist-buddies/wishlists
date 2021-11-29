$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_wishlist_form_data(res) {
    $("#wishlist-id").val(res.id);
    $("#wishlist-name").val(res.name);
    $("#wishlist-user_id").val(res.user_id);
  }

  function update_product_form_data(res) {
    $("#wishlist-product_id").val(res.id);
    $("#wishlist-inventory_product_id").val(res.inventory_product_id);
    $("#wishlist-product_name").val(res.name);
    $("#wishlist-product_price").val(res.price);
    $("#wishlist-product_status").val(res.status);
    $("#wishlist-product_pic").val(res.pic_url);
    $("#wishlist-product_description").val(res.short_desc);
  }

  // Clears all form fields
  function clear_form_data() {
    $("#wishlist-name").val("");
    $("#wishlist-user_id").val("");
    $("#wishlist-product_id").val("");
    $("#wishlist-inventory_product_id").val("");
    $("#wishlist-product_name").val("");
    $("#wishlist-product_price").val("");
    $("#wishlist-product_status").val("");
    $("#wishlist-product_pic").val("");
    $("#wishlist-product_description").val("");
  }

  // Updates the flash message area
  function flash_message(message) {
    $("#flash_message").empty();
    $("#flash_message").append(message);
  }

  // ****************************************
  // Create a Wishlist
  // ****************************************
  $("#create-wishlist").click(function (event) {
    event.preventDefault();
    var name = $("#wishlist-name").val();
    var user_id = $("#wishlist-user_id").val();

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
  // Retrieve a Wishlist
  // ****************************************
  $("#retrieve-wishlist").click(function (event) {
    event.preventDefault();
    var wishlist_id = $("#wishlist-id").val();

    var ajax = $.ajax({
      type: "GET",
      url: `/wishlists/` + wishlist_id,
      contentType: "application/json",
      data: ''
    })

    ajax.done(function(res){
      update_wishlist_form_data(res["data"]);
      flash_message("Success");
      $("#search_results").empty();
      $("#search_results").append('<table class="table-striped" cellpadding="10">');
      var header = '<tr>';
      header += '<th style="width:10%">ID</th>';
      header += '<th style="width:30%">Name</th>';
      header += '<th style="width:10%">User_ID</th>';
      header += '<th style="width:50%">Products</th></tr>';
      $("#search_results").append(header);
      res = res["data"];
      var row = "<tr><td>"+res.id+"</td><td>"+res.name+"</td><td>"+res.user_id+"</td><td>"+res.products+"</td></tr>";
      $("#search_results").append(row);


      $("#search_results").append('</table>');

      // copy the first result to the form
      update_wishlist_form_data(res);
      update_product_form_data(res.products[0]);

      flash_message("Success");
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
    var user_id = $("#wishlist-user_id").val();

    var queryString = "";

    if (user_id) {
      queryString += "user_id=" + user_id;
    }

    var ajax = $.ajax({
      type: "GET",
      url: `/wishlists?`+ queryString,
      contentType: "application/json",
      data: ''
    })

    ajax.done(function(res){
      //alert(res.toSource())
      $("#search_results").empty();
      $("#search_results").append('<table class="table-striped" cellpadding="10">');
      var header = '<tr>';
      header += '<th style="width:10%">ID</th>';
      header += '<th style="width:30%">Name</th>';
      header += '<th style="width:10%">User_ID</th>';
      header += '<th style="width:50%">Products</th></tr>';
      $("#search_results").append(header);
      var firstWishlist = "";
      res = res["data"];
      for(var i = 0; i < res.length; i++) {
        var wishlist = res[i];
        var row = "<tr><td>"+wishlist.id+"</td><td>"+wishlist.name+"</td><td>"+wishlist.user_id+"</td><td>"+wishlist.products+"</td></tr>";
        $("#search_results").append(row);
        if (i == 0) {
          firstWishlist = wishlist;
          }
      }

      $("#search_results").append('</table>');

      // copy the first result to the form
      if (firstWishlist!= "") {
        update_wishlist_form_data(firstWishlist);
      }

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
    })

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
});
