"""
Factory module for generating test data for the shopcart service.

This module provides factories to create fake Shopcart objects for testing
purposes using factory_boy and faker.
"""

import factory
from faker import Faker
from service.models import Shopcart

fake = Faker()

used_shopcart_pairs = set()


class ShopcartFactory(factory.Factory):
    """Creates fake Shopcart entries"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for ShopcartFactory"""

        model = Shopcart

    user_id = None
    item_id = None
    description = factory.LazyFunction(fake.sentence)
    quantity = factory.LazyFunction(lambda: fake.random_int(min=1, max=50))
    price = factory.LazyFunction(lambda: round((fake.random_number(digits=5) / 10), 2))
    created_at = factory.LazyFunction(fake.date_time_this_decade)

    @factory.lazy_attribute
    def last_updated(self):
        """Generate a last_updated attribute"""
        return fake.date_time_between(start_date=self.created_at)

    @staticmethod
    def generate_unique_user_item(user_id=None):
        """Generate a unique (user_id, item_id) pair"""
        while True:
            # If no user_id was provided, generate one.
            if user_id is None:
                user_id = fake.random_int(min=1, max=100)
            item_id = fake.random_int(min=1, max=100)
            if (user_id, item_id) not in used_shopcart_pairs:
                used_shopcart_pairs.add((user_id, item_id))
                return user_id, item_id

    @factory.post_generation
    def assign_unique_user_item(
        self, create, extracted, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Assigns a unique user_id and item_id after object creation.
        If a specific user_id was provided when calling the factory,
        it will be used.
        """

        provided_user_id = self.user_id
        self.user_id, self.item_id = ShopcartFactory.generate_unique_user_item(
            user_id=provided_user_id
        )


def mock_product(**kwargs):
    """
    Mock product data

    Keyword arguments:
        product_id (int): Product ID (default: 111)
        name (str): Product name (default: "Test Product")
        stock (int): Available stock (default: 10)
        purchase_limit (int): Maximum purchase quantity (default: None)
        price (float): Product price (default: 9.99)
        quantity (int): Quantity to add to cart (default: 1)
    """
    # Set default values
    product = {
        "product_id": 111,
        "name": "Test Product",
        "stock": 10,
        "purchase_limit": None,
        "price": 9.99,
        "quantity": 1,
    }

    # Update with provided values
    product.update(kwargs)

    return product
