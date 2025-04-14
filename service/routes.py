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
Shopcarts Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcarts
"""

from flask import jsonify
from flask import current_app as app
from flask_restx import Api, Resource, fields, reqparse
from service.common import status

from service.controllers.get_controller import (
    get_shopcarts_controller,
    get_user_shopcart_controller,
    get_user_shopcart_items_controller,
    get_cart_item_controller,
)

from service.controllers.post_controller import (
    add_product_to_cart_controller,
    add_to_or_create_cart_controller,
    checkout_controller,
)

from service.controllers.put_controller import (
    update_cart_item_controller,
    update_shopcart_controller,
)

from service.controllers.delete_controller import (
    delete_shopcart_controller,
    delete_shopcart_item_controller,
)

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Shopcarts REST API Service",
    description="This is the Shopcarts REST API Service.",
    default="shopcarts",
    default_label="Shopcarts operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# GET INFO
######################################################################
@app.route("/info")
def info():
    """Root URL response with API metadata"""
    app.logger.info("Request for Root URL")

    return (
        jsonify(
            name="Shopcart REST API Service",
            version="1.0",
            paths={
                "/shopcarts": {
                    "GET": "Lists all shopcarts grouped by user",
                },
                "/shopcarts/{user_id}": {
                    "POST": "Adds an item to a user's shopcart or updates quantity if it already exists",
                    "GET": "Retrieves the shopcart with metadata",
                    "PUT": "Updates the entire shopcart",
                    "DELETE": "Deletes the entire shopcart (all items)",
                },
                "/shopcarts/{user_id}/items": {
                    "POST": "Adds a product to a user's shopcart or updates quantity",
                    "GET": "Lists all items in the user's shopcart (without metadata)",
                },
                "/shopcarts/{user_id}/items/{item_id}": {
                    "GET": "Retrieves a specific item from the user's shopcart",
                    "PUT": "Updates a specific item in the shopcart",
                    "DELETE": "Removes an item from the shopcart",
                },
            },
        ),
        status.HTTP_200_OK,
    )


############################################################
# H E A L T H   E N D P O I N T
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


# Define the models for Swagger documentation

shopcart_item_without_timestamps_model = api.model(
    "ShopcartItemWithoutTimestamps",
    {
        "user_id": fields.Integer(required=True, description="The user ID"),
        "item_id": fields.Integer(required=True, description="The item ID"),
        "description": fields.String(required=True, description="The item description"),
        "quantity": fields.Integer(required=True, description="The item quantity"),
        "price": fields.Float(required=True, description="The item price"),
    },
)

shopcart_items_without_timestamps_model = api.model(
    "ShopcartItemsWithoutTimestamps",
    {
        "user_id": fields.Integer(required=True, description="The user ID"),
        "items": fields.List(
            fields.Nested(shopcart_item_without_timestamps_model),
            required=True,
            description="List of items in the cart",
        ),
    },
)

shopcart_item_model = api.model(
    "ShopCartItem",
    {
        "user_id": fields.Integer(required=True, description="The user ID"),
        "item_id": fields.Integer(required=True, description="The item ID"),
        "description": fields.String(
            required=True, description="Description of the item"
        ),
        "quantity": fields.Integer(required=True, description="Quantity of the item"),
        "price": fields.Float(required=True, description="Price of the item"),
        "created_at": fields.DateTime(readOnly=True, description="Creation timestamp"),
        "last_updated": fields.DateTime(
            readOnly=True, description="Last update timestamp"
        ),
    },
)

shopcart_model = api.model(
    "ShopCart",
    {
        "user_id": fields.Integer(required=True, description="The user ID"),
        "items": fields.List(
            fields.Nested(shopcart_item_model), description="Items in the shopcart"
        ),
    },
)

# Define query string arguments for filtering
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "user_id", type=str, location="args", help="Filter by user ID"
)
shopcart_args.add_argument(
    "item_id", type=str, location="args", help="Filter by item ID"
)
shopcart_args.add_argument(
    "description", type=str, location="args", help="Filter by description"
)
shopcart_args.add_argument(
    "quantity",
    type=str,
    location="args",
    help="Filter by quantity or use operators like ~gt~, ~lt~",
)
shopcart_args.add_argument(
    "price",
    type=str,
    location="args",
    help="Filter by price or use operators like ~gt~, ~lt~",
)
shopcart_args.add_argument(
    "created_at", type=str, location="args", help="Filter by creation date"
)
shopcart_args.add_argument(
    "last_updated", type=str, location="args", help="Filter by last update date"
)
shopcart_args.add_argument(
    "price_range",
    type=str,
    location="args",
    help="Filter by price range (format: min,max)",
)
shopcart_args.add_argument(
    "quantity_range",
    type=str,
    location="args",
    help="Filter by quantity range (format: min,max)",
)
shopcart_args.add_argument(
    "min-price", type=float, location="args", help="Filter by minimum price"
)
shopcart_args.add_argument(
    "max-price", type=float, location="args", help="Filter by maximum price"
)
shopcart_args.add_argument(
    "min-qty", type=int, location="args", help="Filter by minimum quantity"
)
shopcart_args.add_argument(
    "max-qty", type=int, location="args", help="Filter by maximum quantity"
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@api.route("/shopcarts", strict_slashes=False)
class ShopcartsCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=False)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """Lists all shopcarts grouped by user"""
        app.logger.info("Request to list all shopcarts")
        return get_shopcarts_controller()


@api.route("/shopcarts/<int:user_id>", strict_slashes=False)
class ShopcartsResource(Resource):
    """Handles all interactions with a single Shopcart resource"""

    @api.doc("get_shopcart")
    @api.expect(shopcart_args, validate=False)
    @api.marshal_with(shopcart_model)
    def get(self, user_id):
        """Gets the shopcart for a specific user id"""
        app.logger.info("Request to get shopcart for user_id: '%s'", user_id)
        return get_user_shopcart_controller(user_id)


@api.route("/shopcarts/<int:user_id>/items", strict_slashes=False)
class ShopcartItemsCollection(Resource):
    """Handles all interactions with the items in a specific user's shopcart"""

    @api.doc("get_shopcart_items")
    @api.marshal_with(shopcart_items_without_timestamps_model)
    def get(self, user_id):
        """Gets all items in a specific user's shopcart"""
        app.logger.info("Request to get all items for user_id: '%s'", user_id)
        return get_user_shopcart_items_controller(user_id)


@api.route("/shopcarts/<int:user_id>/items/<int:item_id>", strict_slashes=False)
class ShopcartItemsResource(Resource):
    """Handles all interactions with a specific item in a shopcart"""

    @api.doc("get_cart_item")
    @api.marshal_with(shopcart_item_model)
    def get(self, user_id, item_id):
        """Gets a specific item from a user's shopcart"""
        app.logger.info("Request to get item %s for user_id: %s", item_id, user_id)
        return get_cart_item_controller(user_id, item_id)


# GET ROUTES


# @app.route("/shopcarts", methods=["GET"])
# def list_shopcarts():
#     """List all shopcarts grouped by user"""
#     return get_shopcarts_controller()


@app.route("/shopcarts/<int:user_id>", methods=["GET"])
def get_user_shopcart(user_id):
    """Gets the shopcart for a specific user id"""
    return get_user_shopcart_controller(user_id)


@app.route("/shopcarts/<int:user_id>/items", methods=["GET"])
def get_user_shopcart_items(user_id):
    """Gets all items in a specific user's shopcart"""
    return get_user_shopcart_items_controller(user_id)


@app.route("/shopcarts/<int:user_id>/items/<int:item_id>", methods=["GET"])
def get_cart_item(user_id, item_id):
    """Gets a specific item from a user's shopcart"""
    return get_cart_item_controller(user_id, item_id)


# POST ROUTES


@app.route("/shopcarts/<int:user_id>", methods=["POST"])
def add_to_or_create_cart(user_id):
    """Add an item to a user's cart or update quantity if it already exists."""
    return add_to_or_create_cart_controller(user_id)


@app.route("/shopcarts/<int:user_id>/items", methods=["POST"])
def add_product_to_cart(user_id):
    """
    Add a product to a user's shopping cart or update quantity if it already exists.
    Product data (name, price, stock, purchase_limit, etc.) is taken from the request body,
    """
    return add_product_to_cart_controller(user_id)


# PUT ROUTES


@app.route("/shopcarts/<int:user_id>/items/<int:item_id>", methods=["PUT"])
def update_cart_item(user_id, item_id):
    """Update a specific item in a user's shopping cart."""
    return update_cart_item_controller(user_id, item_id)


@app.route("/shopcarts/<int:user_id>", methods=["PUT"])
def update_shopcart(user_id):
    """Update an existing shopcart."""
    return update_shopcart_controller(user_id)


# DELETE ROUTES


@app.route("/shopcarts/<int:user_id>", methods=["DELETE"])
def delete_shopcart(user_id):
    """Delete an entire shopcart for a user"""
    return delete_shopcart_controller(user_id)


@app.route("/shopcarts/<int:user_id>/items/<int:item_id>", methods=["DELETE"])
def delete_shopcart_item(user_id, item_id):
    """
    Delete a specific item from a user's shopping cart
    This endpoint removes a single item from a shopping cart while preserving the cart
    and any other items that may be in it
    """
    return delete_shopcart_item_controller(user_id, item_id)


# ACTION ROUTE


@app.route("/shopcarts/<int:user_id>/checkout", methods=["POST"])
def checkout(user_id):
    """Finalize a user's cart and proceed with payment."""
    return checkout_controller(user_id)
