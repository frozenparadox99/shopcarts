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
from unittest.mock import patch
from service.common import status
from .test_routes import TestShopcartService
from .factories import mock_product

######################################################################
#  T E S T   C A S E S
######################################################################


class TestShopcartPost(TestShopcartService):
    """Test cases for post operations"""

    ######################################################################
    #  Post Shopcart Testcase
    ######################################################################
    def test_add_item_creates_new_cart_entry(self):
        """It should create a new cart entry when none exists for the user."""
        user_id = 1
        payload = {
            "item_id": 101,
            "description": "Test Item",
            "price": 9.99,
            "quantity": 2,
        }
        response = self.client.post(f"/api/shopcarts/{user_id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user_id"], user_id)
        self.assertEqual(data[0]["item_id"], payload["item_id"])
        self.assertEqual(data[0]["quantity"], payload["quantity"])
        self.assertAlmostEqual(data[0]["price"], payload["price"], places=2)

    def test_add_item_updates_existing_entry(self):
        """It should update the quantity if the cart entry already exists."""
        user_id = 1
        # First, add the item
        payload = {
            "item_id": 101,
            "description": "Test Item",
            "price": 9.99,
            "quantity": 2,
        }
        response = self.client.post(f"/api/shopcarts/{user_id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        # Add the same item again
        payload2 = {
            "item_id": 101,
            "description": "Test Item",
            "price": 9.99,
            "quantity": 3,
        }
        response2 = self.client.post(f"/api/shopcarts/{user_id}", json=payload2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        data = response2.get_json()
        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        # The quantity should now be 2 + 3 = 5
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["quantity"], 5)
        self.assertAlmostEqual(data[0]["price"], payload["price"], places=2)

    def test_add_item_invalid_input(self):
        """It should return a 400 error if fields have invalid data types."""
        user_id = 1
        # Non-integer 'item_id'
        payload = {"item_id": "abc", "description": "Test Item", "price": 9.99}
        response = self.client.post(f"/api/shopcarts/{user_id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_missing_json(self):
        """It should return 400 when the request body is missing"""
        resp = self.client.post("/api/shopcarts/1", json=[])
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_internal_server_error_update(self):
        """It should return a 500 error when the database update fails"""
        with patch(
            "service.models.Shopcart.update", side_effect=Exception("Database error")
        ):
            user_id = 1
            # First, add the item
            payload = {
                "item_id": 101,
                "description": "Test Item",
                "price": 9.99,
                "quantity": 2,
            }
            response = self.client.post(f"/api/shopcarts/{user_id}", json=payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Add the same item again
            payload2 = {
                "item_id": 101,
                "description": "Test Item",
                "price": 9.99,
                "quantity": 3,
            }
            response2 = self.client.post(f"/api/shopcarts/{user_id}", json=payload2)
            self.assertEqual(
                response2.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_add_item_internal_server_error_create(self):
        """It should return a 500 error when the database creation fails"""
        with patch(
            "service.models.Shopcart.create", side_effect=Exception("Database error")
        ):
            user_id = 1
            # First, add the item
            payload = {
                "item_id": 101,
                "description": "Test Item",
                "price": 9.99,
                "quantity": 2,
            }
            response = self.client.post(f"/api/shopcarts/{user_id}", json=payload)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestAddProductToCart(TestShopcartService):
    """Test cases for add product to cart"""

    ######################################################################
    #  Add Product to Cart Testcase
    ######################################################################

    def test_add_product_to_empty_cart(self):
        """It should add a product to an empty cart if the product is valid."""
        user_id = 1
        payload = mock_product(product_id=111, stock=10, price=9.99, quantity=2)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user_id"], user_id)
        self.assertEqual(data[0]["item_id"], 111)
        self.assertEqual(data[0]["quantity"], 2)
        self.assertAlmostEqual(data[0]["price"], 9.99, places=2)

    def test_add_existing_product_updates_quantity(self):
        """It should update quantity if the product is already in the cart."""
        user_id = 1
        # First add the product
        payload1 = mock_product(product_id=111, stock=10, quantity=2)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload1)

        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        # Add the same product again
        payload2 = mock_product(product_id=111, stock=10, quantity=3)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_url = f"http://localhost/api/shopcarts/{user_id}"
        self.assertIn("Location", response.headers)
        self.assertEqual(response.headers["Location"], expected_url)

        data = response.get_json()
        # Quantity should now be 2 + 3 = 5
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["quantity"], 5)

    def test_add_multiple_distinct_products(self):
        """It should add multiple distinct products to the same cart."""
        user_id = 1
        # Add first product
        payload1 = mock_product(product_id=111, stock=10, quantity=2)
        self.client.post(f"/api/shopcarts/{user_id}/items", json=payload1)

        # Add second product
        payload2 = mock_product(product_id=222, stock=5, quantity=1)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        self.assertEqual(len(data), 2)
        item_ids = [item["item_id"] for item in data]
        self.assertIn(111, item_ids)
        self.assertIn(222, item_ids)

    def test_add_item_out_of_stock(self):
        """It should return a 400 error if the product is out of stock."""
        user_id = 1
        payload = mock_product(product_id=111, stock=0, quantity=1)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_exceeds_stock(self):
        """It should return a 400 error if quantity exceeds available stock."""
        user_id = 1
        payload = mock_product(product_id=111, stock=5, quantity=6)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_exceeds_purchase_limit(self):
        """It should return a 400 error if quantity exceeds the product's purchase limit."""
        user_id = 1
        payload = mock_product(product_id=111, stock=10, purchase_limit=3, quantity=4)
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_missing_fields(self):
        """It should return a 400 error if required fields are missing."""
        user_id = 1
        # Missing 'product_id'
        payload = {
            # "product_id": 111,  # intentionally omitted
            "stock": 10,
            "price": 9.99,
            "quantity": 2,
        }
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_no_payload(self):
        """It should return a 400 error when no JSON payload is provided"""
        user_id = 1
        # Send request with no JSON data
        response = self.client.post(f"/api/shopcarts/{user_id}/items", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_exceeds_stock_when_combined(self):
        """It should return a 400 error if adding more would exceed available stock"""
        user_id = 1
        # First add 3 units of product 111 (with stock of 5)
        initial_payload = mock_product(product_id=111, stock=5, quantity=3)
        self.client.post(f"/api/shopcarts/{user_id}/items", json=initial_payload)

        # Then try to add 3 more units (3 + 3 > 5 stock)
        additional_payload = mock_product(product_id=111, stock=5, quantity=3)
        response = self.client.post(
            f"/api/shopcarts/{user_id}/items", json=additional_payload
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_exceeds_purchase_limit_when_combined(self):
        """It should return a 400 error if adding more would exceed purchase limit"""
        user_id = 1
        # First add 2 units of product 111 (with purchase limit of 3)
        initial_payload = mock_product(
            product_id=111, stock=10, purchase_limit=3, quantity=2
        )
        self.client.post(f"/api/shopcarts/{user_id}/items", json=initial_payload)

        # Then try to add 2 more units (2 + 2 > 3 purchase limit)
        additional_payload = mock_product(
            product_id=111, stock=10, purchase_limit=3, quantity=2
        )
        response = self.client.post(
            f"/api/shopcarts/{user_id}/items", json=additional_payload
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_update_exception(self):
        """It should handle exceptions during cart item update"""
        user_id = 1
        # First add an item to the cart
        initial_payload = mock_product(product_id=111, stock=10, quantity=1)
        self.client.post(f"/api/shopcarts/{user_id}/items", json=initial_payload)

        # Now try to add more of the same item, but mock an exception during update
        with patch(
            "service.models.Shopcart.update", side_effect=Exception("Update error")
        ):
            additional_payload = mock_product(product_id=111, stock=10, quantity=1)
            response = self.client.post(
                f"/api/shopcarts/{user_id}/items", json=additional_payload
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_create_exception(self):
        """It should handle exceptions during cart item creation"""
        user_id = 1
        # Try to add a new item, but mock an exception during creation
        with patch(
            "service.models.Shopcart.create", side_effect=Exception("Create error")
        ):
            payload = mock_product(product_id=111, stock=10, quantity=1)
            response = self.client.post(f"/api/shopcarts/{user_id}/items", json=payload)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
