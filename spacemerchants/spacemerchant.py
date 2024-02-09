
import asyncio
from datetime import datetime

from pprint import pprint

from loguru import logger
from spacemerchants.models.agent import Agent

from spacemerchants.models.faction import Faction

from spacetradercore.spacemerchantcore import SpaceMerchantCore

logger.add("spacemerchants.log", level="TRACE", rotation="1 day", retention="14 days")

SPACETRADER_API_URL = "https://api.spacetraders.io/v2/"
SPACETRADER_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGlmaWVyIjoiUkhZVEhNLVRFU1QiLCJ2ZXJzaW9uIjoidjIuMS41IiwicmVzZXRfZGF0ZSI6IjIwMjQtMDEtMjgiLCJpYXQiOjE3MDcxMDY1MjYsInN1YiI6ImFnZW50LXRva2VuIn0.mKP-HSd3ZLM6QvP6QuhV7qj0EFR7IncIZ-TxnosmrU5ZFyccI9CVZ9DKHwQUFCY9Zz2W46qSP-ovZAQhiP8bs_G9IXkmjmrrdpEDuC-oQTlk9m1L-rfaVaI4v8cy61yUhZBwR5V0nzOqUPPkfJWq2Hnk-JIMWx4PzmsJs_-UKJ742n2hs52jiWF3NuiEnUUwNE-h8aPleUUkP55cLMaswtv9WTbasU27WH5Wgi5_pu71en9sYR1CcAAl0DEVj6ekciqmsRBM7KwvH6RwDsXpo9VjAhXEy_kua2YqzgzsvAfr-aFLSsPF7WiRDOYzV3wgLgeITq_W8UoUxnRm7ZAPIw"


class SpaceMerchants:
    """A class to interact with the SpaceTraders API"""

    last_reset: datetime
    next_reset: datetime
    frequency: str
    version: str
    _factions: list[Faction] = []

    _headers = {
        "Content-Type": "application/json",
    }

    def __init__(self, key: str):
        self.key = key

    async def __aenter__(self):
        # create a new session
        self.requester = SpaceMerchantCore(key=self.key)
        await self.requester.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # close the session
        await self.requester.close()

    async def register(self, callsign: str, faction: str, email: str = ""):
        """Register a new user with the SpaceTrader API

        Args:
            callsign (str): The name of the user
            faction (str): The faction the user wants to join
        """
        logger.debug(f"SpaceMerchant | register | {callsign =:} | {faction =:} | {email =:}")
        pass

    async def status(self):
        """Get the status of the SpaceTrader API"""
        logger.debug("SpaceMerchant | status")
        response = await self.requester.status()
        logger.trace(f"SpaceMerchant | status | {response}")
        self.last_reset = datetime.fromisoformat(response["resetDate"])
        self.next_reset = datetime.fromisoformat(
            response.get("serverResets", {}).get("next")
        )
        self.frequency = response["serverResets"]["frequency"]
        self.status_message = response["status"]
        self.version = response["version"]
        logger.debug(f"SpaceMerchant | status | {self.status_message = :} | {self.last_reset = :} | "
                     f"{self.next_reset = :} | {self.frequency = :} | {self.version = :}")

    async def me(self) -> Agent:
        """Get the user's information"""
        logger.debug("SpaceMerchant | me")
        response = await self.requester.get_agent()
        return await Agent.from_dict(self.requester, response.get("data", {}))

    async def factions(self):
        """Get the list of factions available"""
        if self._factions:
            return self._factions
        async with SpaceMerchantCore(key=self.key) as requester:
            response = await requester.get_factions()
        logger.debug(f"SpaceMerchant | factions | {response}")
        self._factions = [Faction.from_dict(faction) for faction in response.get("data", [])]
        return self._factions

    def __str__(self):
        return (
            f"SpaceTraders API Status: {self.status_message}\nLast Reset: {self.last_reset}\nNext Reset: "
            f"{self.next_reset}\nFrequency: {self.frequency}\nVersion: {self.version}"
        )


async def main():
    spacemerchant = SpaceMerchants(SPACETRADER_KEY)
    async with spacemerchant as sm:
        x = await sm.factions()
        pprint(x)

if __name__ == "__main__":
    sm = SpaceMerchants(SPACETRADER_KEY)
    # asyncio.run(sm.register("RHYTHM-TEST", "COSMIC"))

    asyncio.run(main())
