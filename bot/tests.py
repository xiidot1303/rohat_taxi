from django.test import SimpleTestCase

from app.models import FavoriteAddress
from bot.bot.settings import _favorite_addresses_menu_text


class FavoriteAddressSettingsTests(SimpleTestCase):
    def test_favorite_addresses_menu_text_includes_address_details(self):
        class DummyWords:
            favorite_addresses = "Sevimli manzillar"
            favorite_address_no_addresses = "Hozircha saqlangan manzillar yo'q"

        class DummyContext:
            words = DummyWords()

        address = FavoriteAddress(address="Home", lat="41.3", lon="69.2")

        text = _favorite_addresses_menu_text([address], DummyContext())

        self.assertIn("Home", text)
        self.assertIn("41.3", text)
        self.assertIn("69.2", text)
