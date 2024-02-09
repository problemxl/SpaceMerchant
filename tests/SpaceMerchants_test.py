from spacemerchants.spacemerchant import SpaceMerchants

from unittest import IsolatedAsyncioTestCase
import asyncio

class TestSpaceMerchants(IsolatedAsyncioTestCase):

    async def test_me(self):
        sm = SpaceMerchants()
        await sm.me()
        self.assertIsNotNone(sm.account_id)
        self.assertIsNotNone(sm.symbol)
        self.assertIsNotNone(sm.headquarters)
        self.assertIsNotNone(sm.credits)
        self.assertIsNotNone(sm.faction)
        self.assertIsNotNone(sm.ship_count)
        self.assertGreater(sm.ship_count, 0)