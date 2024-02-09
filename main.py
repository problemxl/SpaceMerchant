import asyncio
from spacemerchants.models.system import System
from spacemerchants.spacemerchant import SpaceMerchantCore
from spacemerchants.spacemerchant import SpaceMerchants

from loguru import logger

SPACETRADER_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGlmaWVyIjoiUkhZVEhNLVRFU1QiLCJ2ZXJzaW9uIjoidjIuMS41IiwicmVzZXRfZGF0ZSI6IjIwMjQtMDEtMjgiLCJpYXQiOjE3MDcxMDY1MjYsInN1YiI6ImFnZW50LXRva2VuIn0.mKP-HSd3ZLM6QvP6QuhV7qj0EFR7IncIZ-TxnosmrU5ZFyccI9CVZ9DKHwQUFCY9Zz2W46qSP-ovZAQhiP8bs_G9IXkmjmrrdpEDuC-oQTlk9m1L-rfaVaI4v8cy61yUhZBwR5V0nzOqUPPkfJWq2Hnk-JIMWx4PzmsJs_-UKJ742n2hs52jiWF3NuiEnUUwNE-h8aPleUUkP55cLMaswtv9WTbasU27WH5Wgi5_pu71en9sYR1CcAAl0DEVj6ekciqmsRBM7KwvH6RwDsXpo9VjAhXEy_kua2YqzgzsvAfr-aFLSsPF7WiRDOYzV3wgLgeITq_W8UoUxnRm7ZAPIw"

async def tutorial1():
    async with SpaceMerchants(SPACETRADER_KEY) as sm:
        await sm.status()
        agent = await sm.me()
        system = await System.get(sm.requester, agent.headquarters[:-3])
        print(system)
        # waypoints = await system.waypoints()
        # for waypoint in waypoints:
        #     print(waypoint)
        contracts = await agent.contracts()
        for contract in contracts:
            print(contract)

        ships = await agent.get_ships()
        for ship in ships:
            logger.info(f"{ship =:} | waypoint = {ship.navigation.waypoint_symbol}")



        for waypoint in await system.shipyard():
            print(waypoint)

asyncio.run(tutorial1())
