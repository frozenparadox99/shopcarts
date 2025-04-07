$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#user_id").val(res.user_id);
        $("#item_id").val(res.item_id);
        $("#item_description").val(res.description);
        $("#item_price").val(res.price);
        $("#item_quantity").val(res.quantity);
        $("#item_created_at").val(res.created_at);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#item_id").val("");
        $("#item_description").val("");
        $("#item_price").val("");
        $("#item_quantity").val("");
        $("#item_created_at").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create / Add Item to Cart
    // ****************************************

    $("#create-btn").click(function () {
        let user_id = $("#user_id").val();
        let item_id = $("#item_id").val();
        let description = $("#item_description").val();
        let price = $("#item_price").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "item_id": parseInt(item_id),
            "description": description,
            "price": parseFloat(price),
            "quantity": parseInt(quantity)
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/shopcarts/${user_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            if (res.length > 0) {
                // Find the item we just added
                let added_item = res.find(item => item.item_id == item_id);
                if (added_item) {
                    update_form_data(added_item);
                }
            }
            flash_message("Item successfully added to cart!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.error || "Server error!");
        });
    });

    // ****************************************
    // Update an Item in Cart
    // ****************************************

    $("#update-btn").click(function () {
        let user_id = $("#user_id").val();
        let item_id = $("#item_id").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "quantity": parseInt(quantity)
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${user_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            if (res.message) {
                // Item was removed (quantity set to 0)
                clear_form_data();
                flash_message(res.message);
            } else {
                update_form_data(res);
                flash_message("Item updated successfully!");
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.error || "Server error!");
        });
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {
        let user_id = $("#user_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${user_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            // Display the cart items in the search results table
            $("#search_results").empty();
            let table = '<table class="table table-striped">';
            table += '<thead><tr>';
            table += '<th class="col-md-1">User ID</th>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-4">Description</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '<th class="col-md-1">Quantity</th>';
            table += '<th class="col-md-2">Created At</th>';
            table += '</tr></thead><tbody>';

            // Flatten items from all carts
            let items = [];
            for (let cart of res) {
                for (let item of cart.items) {
                    items.push(item);
                }
            }

            let firstItem = null;
            for(let i = 0; i < items.length; i++) {
                let item = items[i];
                table += `<tr id="row_${i}">
                    <td>${item.user_id}</td>
                    <td>${item.item_id}</td>
                    <td>${item.description}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td>${item.quantity}</td>
                    <td>${item.created_at}</td>
                </tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // Copy the first result to the form
            if (firstItem) {
                update_form_data(firstItem);
                flash_message("Shopcart retrieved successfully!");
            } else {
                flash_message("No items found in shopcart.");
            }
        });

        ajax.fail(function(res){
            clear_form_data();
            if (res.status == 404) {
                flash_message("Shopcart not found for this user.");
            } else {
                flash_message(res.responseJSON.error || "Server error!");
            }
        });
    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {
        let user_id = $("#user_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${user_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            $("#search_results").empty();
            flash_message("Shopcart has been deleted!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.error || "Server error!");
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#user_id").val("");
        clear_form_data();
        $("#flash_message").empty();
    });

    // ****************************************
    // Search for Shopcarts
    // ****************************************

    $("#search-btn").click(function () {
        let user_id = $("#user_id").val();
        let item_id = $("#item_id").val();
        let price = $("#item_price").val();
        let quantity = $("#item_quantity").val();

        let queryString = "";

        if (user_id) {
            queryString += 'user_id=' + user_id;
        }
        
        if (item_id) {
            if (queryString.length > 0) {
                queryString += '&item_id=' + item_id;
            } else {
                queryString += 'item_id=' + item_id;
            }
        }
        
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price;
            } else {
                queryString += 'price=' + price;
            }
        }
        
        if (quantity) {
            if (queryString.length > 0) {
                queryString += '&quantity=' + quantity;
            } else {
                queryString += 'quantity=' + quantity;
            }
        }

        $("#flash_message").empty();

        // Default search URL if no queryString
        let searchUrl = "/shopcarts";
        if (queryString.length > 0) {
            searchUrl += "?" + queryString;
        }

        let ajax = $.ajax({
            type: "GET",
            url: searchUrl,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped">';
            table += '<thead><tr>';
            table += '<th class="col-md-1">User ID</th>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-4">Description</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '<th class="col-md-1">Quantity</th>';
            table += '<th class="col-md-2">Created At</th>';
            table += '</tr></thead><tbody>';

            // Flatten items from all carts
            let items = [];
            for (let cart of res) {
                for (let item of cart.items) {
                    items.push(item);
                }
            }

            let firstItem = null;
            for(let i = 0; i < items.length; i++) {
                let item = items[i];
                table += `<tr id="row_${i}">
                    <td>${item.user_id}</td>
                    <td>${item.item_id}</td>
                    <td>${item.description}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td>${item.quantity}</td>
                    <td>${item.created_at}</td>
                </tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // Copy the first result to the form
            if (firstItem) {
                update_form_data(firstItem);
                flash_message("Search results found!");
            } else {
                flash_message("No items found matching the search criteria.");
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.error || "Server error!");
        });
    });
});
