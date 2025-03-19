######################################################################
# Copyright 2016, 2024 John J.
# Rofrano. All Rights Reserved.
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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Shopcart
from .factories import ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################


class TestShopcartService(TestCase):
    """Test cases for the Shopcart Service"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Configure your test database here
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "postgresql+psycopg2://postgres:postgres@localhost:5432/testdb"
        )
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # Clean up any leftover data
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################
    def _populate_shopcarts(self, count=5, user_id=None, quantity=None, price=None):
        """Create and populate shopcarts in the database using ShopcartFactory"""
        shopcarts = []
        for _ in range(count):
            attrs = {}

            if user_id is not None:
                attrs["user_id"] = user_id
            if quantity is not None:
                attrs["quantity"] = quantity
            if price is not None:
                attrs["price"] = price

            shopcart = ShopcartFactory(**attrs)
            payload = {
                "item_id": shopcart.item_id,
                "description": shopcart.description,
                "price": float(shopcart.price),
                "quantity": shopcart.quantity,
            }
            response = self.client.post(f"/shopcarts/{shopcart.user_id}", json=payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            shopcarts.append(shopcart)
        return shopcarts

    ######################################################################
    #  T E S T   C A S E S   F O R   C H E C K O U T
    ######################################################################
    def test_checkout_success(self):
        """It should finalize a cart successfully when items exist."""
        user_id = 1
        # Pre-populate the cart with 2 items
        self._populate_shopcarts(count=2, user_id=user_id)

        # Call the checkout endpoint
        response = self.client.post(f"/shopcarts/{user_id}/checkout")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("total_price", data)

    def test_checkout_empty_cart(self):
        """It should return 400 if the cart is empty."""
        user_id = 2
        response = self.client.post(f"/shopcarts/{user_id}/checkout")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("error", data)

    def test_checkout_already_checked_out(self):
        """It should return 400 if the cart is already checked out."""
        user_id = 3
        # Pre-populate with 1 item
        self._populate_shopcarts(count=1, user_id=user_id)

        # First checkout call (should succeed)
        first_checkout = self.client.post(f"/shopcarts/{user_id}/checkout")
        self.assertEqual(first_checkout.status_code, status.HTTP_200_OK)

        # Second checkout call
        second_checkout = self.client.post(f"/shopcarts/{user_id}/checkout")
        self.assertEqual(second_checkout.status_code, status.HTTP_400_BAD_REQUEST)
        data = second_checkout.get_json()
        self.assertIn("error", data)
