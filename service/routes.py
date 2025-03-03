######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart
from service.common import status  # HTTP Status Codes
import requests
from .config import PRODUCT_SERVICE_URL
######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


@app.route("/shopcart/<int:user_id>", methods=["POST"])
def add_to_or_create_cart(user_id):
    """Add an item to a user's cart or update quantity if it already exists."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), status.HTTP_400_BAD_REQUEST

    try:
        item_id = int(data["item_id"])
        description = str(data["description"])
        price = float(data["price"])
        quantity = int(data.get("quantity", 1))
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), status.HTTP_400_BAD_REQUEST

    # Check if this item is already in the user's cart
    cart_item = Shopcart.find(user_id, item_id)
    if cart_item:
        # Update the existing item's quantity
        cart_item.quantity += quantity
        try:
            cart_item.update()
        except Exception as e:
            return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST
    else:
        # Create a new cart entry
        new_item = Shopcart(
            user_id=user_id,
            item_id=item_id,
            description=description,
            quantity=quantity,
            price=price,
        )
        try:
            new_item.create()
        except Exception as e:
            return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST

    # Return the updated cart for the user
    cart = [item.serialize() for item in Shopcart.find_by_user_id(user_id)]
    return jsonify(cart), status.HTTP_200_OK


@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """List all shopcarts grouped by user"""
    app.logger.info("Request to list shopcarts")

    try:
        # Initialize an empty list to store unique user shopcarts
        shopcarts_list = []

        # Get all shopcarts grouped by user_id
        all_items = Shopcart.all()

        # Group items by user_id
        user_items = {}
        for item in all_items:
            if item.user_id not in user_items:
                user_items[item.user_id] = []
            user_items[item.user_id].append(item.serialize())

        # Create the response list
        for user_id, items in user_items.items():
            shopcarts_list.append({"user_id": user_id, "items": items})

        return jsonify(shopcarts_list), status.HTTP_200_OK

    except Exception as e:
        app.logger.error(f"Error listing shopcarts: {str(e)}")
        return (
            jsonify({"error": f"Internal server error: {str(e)}"}),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/shopcarts/<int:user_id>", methods=["GET"])
def get_user_shopcart(user_id):
    """Gets the shopcart for a specific user id"""
    app.logger.info("Request to get shopcart for user_id: '%s'", user_id)

    try:

        user_items = Shopcart.find_by_user_id(user_id=user_id)
        for i in user_items:
            print(i.serialize())

        if not user_items:
            return jsonify([]), status.HTTP_404_NOT_FOUND

        user_list = [{"user_id": user_id, "items": []}]
        for item in user_items:
            user_list[0]["items"].append(item.serialize())
        return jsonify(user_list), status.HTTP_200_OK

    except Exception as e:
        app.logger.error(f"Error reading shopcart for user_id: '{user_id}'")
        return (
            jsonify({"error": f"Internal server error: {str(e)}"}),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/shopcarts/<int:user_id>/items", methods=["POST"])
def add_product_to_cart(user_id):
    """
    Add a product to a user's shopping cart or update quantity if it already exists.
    Retrieves product info (stock, purchase limit, etc.) from an external microservice.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), status.HTTP_400_BAD_REQUEST

    try:
        product_id = int(data["product_id"])
        quantity = int(data.get("quantity", 1))
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), status.HTTP_400_BAD_REQUEST

    product_data = fetch_product_info(product_id)
    if product_data is None:
        return jsonify({"error": "Product does not exist"}), status.HTTP_404_NOT_FOUND

    if product_data["stock"] < 1:
        return jsonify({"error": "Product is out of stock"}), status.HTTP_400_BAD_REQUEST

    if quantity > product_data["stock"]:
        return (
            jsonify({"error": f"Only {product_data['stock']} units are available"}),
            status.HTTP_400_BAD_REQUEST,
        )

    purchase_limit = product_data.get("purchase_limit")
    if purchase_limit is not None and quantity > purchase_limit:
        return (
            jsonify({"error": f"Cannot exceed purchase limit of {purchase_limit}"}),
            status.HTTP_400_BAD_REQUEST,
        )

    cart_item = Shopcart.find(user_id, product_id)
    if cart_item:
        new_quantity = cart_item.quantity + quantity
        # Re-check stock and limit for the new total
        if new_quantity > product_data["stock"]:
            return (
                jsonify({"error": f"Cannot exceed {product_data['stock']} units in stock"}),
                status.HTTP_400_BAD_REQUEST,
            )
        if purchase_limit is not None and new_quantity > purchase_limit:
            return (
                jsonify({"error": f"Cannot exceed purchase limit of {purchase_limit}"}),
                status.HTTP_400_BAD_REQUEST,
            )
        cart_item.quantity = new_quantity
        try:
            cart_item.update()
        except Exception as e:
            app.logger.error("Error updating cart item: %s", e)
            return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST
    else:
        # Create a new cart item
        new_item = Shopcart(
            user_id=user_id,
            item_id=product_id,
            description=product_data["name"], 
            quantity=quantity,
            price=product_data["price"], 
        )
        try:
            new_item.create()
        except Exception as e:
            app.logger.error("Error creating cart item: %s", e)
            return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST

    cart_items = Shopcart.find_by_user_id(user_id)
    return jsonify([item.serialize() for item in cart_items]), status.HTTP_200_OK


def fetch_product_info(product_id):
    """
    Retrieves product data from the external product microservice.
    """
    try:
        # Example GET endpoint: /api/products/<product_id>
        url = f"{PRODUCT_SERVICE_URL}/{product_id}"
        response = requests.get(url, timeout=3)  # 3-second timeout
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()  # Expected to return the product data in JSON
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling product microservice: {e}")
        return None
