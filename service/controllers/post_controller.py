"""
POST Controller logic for Shopcart Service
"""

from flask import request
from flask import current_app as app

from service.common import status
from service.common.helpers import (
    validate_request_data,
    validate_stock_and_limits,
    update_or_create_cart_item,
)
from service.models import Shopcart, DataValidationError


def add_to_or_create_cart_controller(user_id):
    """Add a product to a user's shopping cart or update quantity if it already exists."""
    data = request.get_json()
    if not data:
        return "Missing JSON payload", status.HTTP_400_BAD_REQUEST

    try:
        item_id = int(data["item_id"])
        description = str(data["description"])
        price = float(data["price"])
        quantity = int(data.get("quantity", 1))
    except (KeyError, ValueError, TypeError) as e:
        return f"Invalid input: {e}", status.HTTP_400_BAD_REQUEST

    # Check if this item is already in the user's cart
    cart_item = Shopcart.find(user_id, item_id)
    if cart_item:
        # Update the existing item's quantity
        cart_item.quantity += quantity
        try:
            cart_item.update()
        except Exception as e:  # pylint: disable=broad-except
            return (
                {"error": f"Internal server error: {str(e)}"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
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
        except Exception as e:  # pylint: disable=broad-except
            return (
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Return the updated cart for the user
    cart = [item.serialize() for item in Shopcart.find_by_user_id(user_id)]
    return cart, status.HTTP_201_CREATED


def add_product_to_cart_controller(user_id):
    """Add a product to a user's shopping cart or update quantity if it already exists."""
    data = request.get_json()
    if not data:
        return "Missing JSON payload", status.HTTP_400_BAD_REQUEST

    try:
        product_id, quantity, name, price, stock, purchase_limit = (
            validate_request_data(data)
        )
    except ValueError as e:
        return str(e), status.HTTP_400_BAD_REQUEST

    error_response = validate_stock_and_limits(quantity, stock, purchase_limit)
    if error_response:
        return error_response

    # Look for an existing cart item (composite key: user_id & product_id)
    try:
        product_data = {
            "product_id": product_id,
            "quantity": quantity,
            "name": name,
            "price": price,
            "stock": stock,
            "purchase_limit": purchase_limit,
        }
        cart_items = update_or_create_cart_item(user_id, product_data)
    except Exception as e:  # pylint: disable=broad-except
        app.logger.error("Cart update error: %s", e)
        return str(e), status.HTTP_400_BAD_REQUEST

    return ([item.serialize() for item in cart_items], status.HTTP_201_CREATED)


def checkout_controller(user_id):
    """Finalize a user's cart and proceed with payment."""
    try:
        total_price = Shopcart.finalize_cart(user_id)
        return (
            {
                "message": f"Cart {user_id} checked out successfully",
                "total_price": total_price,
            },
            status.HTTP_200_OK,
        )

    except DataValidationError as e:
        return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

    except Exception as e:  # pylint: disable=broad-except
        app.logger.error("Checkout error for user %s: %s", user_id, e)
        return (
            {"error": f"Internal server error: {str(e)}"},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
