import asyncio
from datetime import datetime
from pprint import pprint

from loguru import logger

from spacemerchants.models.ship import Ship
from spacetradercore.spacemerchantcore import SpaceMerchantCore


class Term:
    deadline: datetime
    amount_upfront: int
    amount_due: int
    deliver: dict

    @classmethod
    def from_dict(cls, data: dict) -> "Term":
        term = cls()
        term.deadline = data["deadline"]
        term.amount_upfront = data["amountUpfront"]
        term.amount_due = data["amountDue"]
        term.deliver = data["deliver"]
        return term


class Contract:
    id: str
    faction: str
    type: str
    term: Term
    accepted: bool
    fulfilled: bool
    expiration: datetime
    deadline_to_accept: datetime
    _requester: SpaceMerchantCore

    @classmethod
    def from_dict(cls, requester: SpaceMerchantCore, data: dict) -> "Contract":
        contract = cls()
        contract._requester = requester
        contract.id = data["id"]
        contract.faction = data["faction"]
        contract.type = data["type"]
        contract.term = Term.from_dict(data["term"])
        contract.accepted = data["accepted"]
        contract.fulfilled = data["fulfilled"]
        contract.expiration = data["expiration"]
        contract.deadline_to_accept = data["deadlineToAccept"]
        return contract

    async def accept(self):
        """Accept the contract"""
        response = await self._requester.accept_contract(self.id)
        return response

    async def fulfill(self):
        """Fulfill the contract"""
        response = await self._requester.fulfill_contract(self.id)
        return response
    
    def __str__(self):
        return f"Contract({self.id}, {self.faction}, {self.type}, {self.accepted}, {self.fulfilled})"


class Agent:
    """A class that represents an agent in the SpaceTraders game"""

    account_id: str
    symbol: str
    headquarters: str
    credits: int
    faction: str
    ship_count: int
    _requester: SpaceMerchantCore
    _ships: list[Ship] = []
    _contracts: list[Contract] = []

    def __init__(self, requester: SpaceMerchantCore):
        self._requester = requester

    @classmethod
    async def me(cls):
        """Get the details of the current user"""
        raise NotImplementedError

    @classmethod
    async def from_dict(cls, requester: SpaceMerchantCore, data: dict):
        """Create a new Agent object from a dictionary"""
        agent = cls(requester)
        agent.account_id = data.get("account_id", "")
        agent.symbol = data.get("symbol", "")
        agent.headquarters = data.get("headquarters", "")
        agent.credits = data.get("credits", 0)
        agent.faction = data.get("faction", "")
        agent.ship_count = data.get("shipCount", 0)
        return agent

    async def get_ships(self, force: bool = False):
        """Get the details of the current user's ships"""
        if not force and self._ships:
            return self._ships
        limit = 20
        page = 1
        while True:
            logger.debug(f"Agent | get_ships | {limit =:} | {page =:}")
            response = await self._requester.list_ships(limit=limit, page=page)
            logger.debug(f"Agent | get_ships | {response =:}")
            ships = response.get("data", [])
            meta = response.get("meta", {})
            self._ships.extend([Ship.from_dict(self._requester, ship) for ship in ships])
            logger.debug(f"Agent | get_ships | {len(self._ships) =:} | {meta =:}")
            if meta.get("total") == len(self._ships):
                break
            page += 1
        return self._ships

    async def contracts(self, force: bool = False):
        """Get the contracts for the current user

        Args:
            force (bool, optional): Force a refresh of the contracts. Defaults to False.
        """
        if not force and self._contracts:
            return self._contracts
        limit = 20
        page = 1
        while True:
            response = await self._requester.list_contracts(limit=limit, page=page)
            logger.debug(f"Agent | contracts | {response =:}")
            contracts = response.get("data", [])
            meta = response.get("meta", {})
            self._contracts.extend([Contract.from_dict(self._requester, contract) for contract in contracts])
            if meta.get("total") == len(self._contracts):
                break
            page += 1
        return self._contracts

    def __str__(self):
        return f"Agent({self.symbol}, {self.faction}, {self.credits}, {self.ship_count}, {self.headquarters})"


async def main():
    async with SpaceMerchantCore(key=SPACETRADER_API_KEY) as requester:
        agent = Agent(requester)
        await agent.get_ships()
        pprint(agent._ships)


if __name__ == "__main__":
    asyncio.run(main())
