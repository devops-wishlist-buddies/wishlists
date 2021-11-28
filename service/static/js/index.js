$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_wishlist_form_data(res) {
    $("#wishlist_id").val(res.id);
    $("#wishlist_name").val(res.name);
    $("#wishlist_user_id").val(res.user_id);
  }

  // Clears all form fields
  function clear_form_data() {
    $("#wishlist_name").val("");
    $("#wishlist_user_id").val("");
  }

  // Updates the flash message area
  function flash_message(message) {
    $("#flash_message").empty();
    $("#flash_message").append(message);
  }

  // ****************************************
  // Create a Wishlist
  // ****************************************
  $("#create-wishlist").click(function () {
    var name = $("#wishlist_name").val();
    var user_id = $("#wishlist_user_id").val();

    var data = {
      "name": name,
      "user_id": Number(user_id),
    };

    var ajax = $.ajax({
        type: "POST",
        url: "http://localhost:3000/wishlists",
        contentType:"application/json",
        data: JSON.stringify(data),
    });

    ajax.done(function(res){
      update_wishlist_form_data(res["data"])
      flash_message(res["message"])
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message)
    });
  });

  // ****************************************
  // Retrieve a Wishlist
  // ****************************************
  $("#search-wishlist").click(function () {

    var wishlist_id = $("#wishlist_id").val();

    var ajax = $.ajax({
      type: "GET",
      url: "/wishlists/" + wishlist_id,
      contentType: "application/json",
      data: ''
    })

    ajax.done(function(res){
      update_wishlist_form_data(res["data"])
      flash_message("Success")
    });

    ajax.fail(function(res){
      flash_message(res.responseJSON.message)
    });

  });

  // ****************************************
  // Clear the form
  // ****************************************
  $("#wishlists_clear").click(function () {
    $("#wishlist_id").val("");
    clear_form_data()
  });

});
