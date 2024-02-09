from unittest import IsolatedAsyncioTestCase

from spacemerchants.models.agent import Agent


# test the Agent class
class TestAgent(IsolatedAsyncioTestCase):

    async def test_me(self):
        agent = Agent()
        await agent.me()
        self.assertIsNotNone(agent.account_id)
        self.assertIsNotNone(agent.symbol)
        self.assertIsNotNone(agent.headquarters)
        self.assertIsNotNone(agent.credits)
        self.assertIsNotNone(agent.faction)
        self.assertIsNotNone(agent.ship_count)
        self.assertGreater(agent.ship_count, 0)
