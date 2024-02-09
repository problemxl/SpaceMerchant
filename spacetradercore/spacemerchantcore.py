from aiohttp import ClientSession

from spacetradercore.rate_limit import AsyncRateLimiter
from spacetradercore.constants import SPACETRADER_BASE_URL

from loguru import logger


class SpaceMerchantCore:
    """A class to interact with the SpaceTraders API"""

    _headers = {
        "Content-Type": "application/json",
    }

    def __init__(self, key: str = ""):
        self.key = key
        self.rate_limiter = AsyncRateLimiter(2, 1)

    async def __aenter__(self) -> "SpaceMerchantCore":
        # create a new session
        logger.debug("SpaceMerchantCore | __aenter__")
        self._headers["Authorization"] = f"Bearer {self.key}"
        self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # close the session
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    async def _post(self, endpoint: str = "", data: dict = {}) -> dict:
        """Send a POST request to the SpaceTraders API

        Args:
            url (str): The URL to send the request to
            data (dict): The data to send with the request
        """
        async with self.session.post(
            SPACETRADER_BASE_URL + endpoint, headers=self._headers, json=data
        ) as response:
            return await response.json()

    async def _get(self, endpoint: str = "", params: dict = {}) -> dict:
        """Send a GET request to the SpaceTraders API

        Args:
            url (str): The URL to send the request to
        """
        async with self.rate_limiter.throttle():
            async with self.session.get(
                SPACETRADER_BASE_URL + endpoint, headers=self._headers, params=params
            ) as response:
                return await response.json()

    async def _patch(self, endpoint: str = "", data: dict = {}) -> dict:
        """Send a PUT request to the SpaceTraders API

        Args:
            endpoint (str): The endpoint to send the request to
            data (dict): The data to send with the request
        """
        async with self.rate_limiter.throttle():
            async with self.session.patch(
                SPACETRADER_BASE_URL + endpoint, headers=self._headers, json=data
            ) as response:
                return await response.json()

    async def _delete(self, endpoint: str = "") -> dict:
        """Send a DELETE request to the SpaceTraders API

        Args:
            endpoint (str): The URL to send the request to
        """
        async with self.rate_limiter.throttle():
            async with self.session.delete(
                SPACETRADER_BASE_URL + endpoint, headers=self._headers
            ) as response:
                return await response.json()

    async def register(self, callsign: str, faction: str = "COSMIC", email: str = ""):
        """Register a new user with the SpaceTrader API

        Args:
            callsign (str): The name of the user
            faction (str): The faction the user wants to join
            email (str): The email of the user
        """
        data = {"username": callsign, "faction": faction, "email": email}
        return await self._post(endpoint="register", data=data)

    async def status(self):
        """Get the status of the SpaceTrader API"""
        return await self._get("")

    async def get_agent(self):
        """Get the user's information"""
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the user's information")
        return await self._get(endpoint="my/agent")

    async def list_agents(self, limit: int = 20, page: int = 1):
        """Get the list of agents"""
        params = {"limit": limit, "page": page}
        return await self._get(endpoint="agents", params=params)

    async def get_public_agent(self, agent_symbol: str):
        """Get the public information of an agent

        Args:
            agent_symbol (str): The symbol of the agent to get the information of
        """
        return await self._get(endpoint="agents", params={"agentSymbol": agent_symbol})

    async def list_contracts(self, limit: int = 20, page: int = 1):
        """Get the list of contracts

        Args:
            limit (int): The number of contracts to get
            page (int): The page of contracts to get
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the list of contracts")
        params = {"limit": limit, "page": page}
        return await self._get(endpoint="my/contracts", params=params)

    async def get_contract(self, contract_id: str):
        """Get the information of a contract

        Args:
            contract_id (str): The ID of the contract to get the information of
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the contract information")
        return await self._get(endpoint=f"my/contracts/{contract_id}")

    async def accept_contract(self, contract_id: str):
        """Accept a contract

        Args:
            contract_id (str): The ID of the contract to accept
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to accept a contract")
        return await self._post(endpoint=f"my/contracts/{contract_id}/accept")

    async def deliver_cargo_to_contract(
        self, contract_id: str, ship_symbol: str, trade_symbol: str, units: int
    ):
        """Deliver cargo to a contract

        Args:
            contract_id (str): The ID of the contract to deliver cargo to
            ship_symbol (str): The symbol of the ship to deliver cargo with
            trade_symbol (str): The symbol of the trade good to deliver
            units (int): The number of units to deliver
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to deliver cargo to a contract")
        data = {"shipId": ship_symbol, "good": trade_symbol, "quantity": units}
        return await self._post(endpoint=f"my/contracts/{contract_id}/deliver", data=data)

    async def fulfill_contract(self, contract_id: str) -> dict:
        """Fulfill a contract

        Args:
            contract_id (str): The ID of the contract to fulfill
            trade_symbol (str): The symbol of the trade good to deliver
            units (int): The number of units to deliver
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to fulfill a contract")
        return await self._post(endpoint=f"my/contracts/{contract_id}/fulfill")

    async def get_factions(self, limit: int = 20, page: int = 1):
        """Get the list of factions

        Args:
            limit (int): The number of factions to get
            page (int): The page of factions to get
        """
        params = {"limit": limit, "page": page}
        return await self._get(endpoint="factions", params=params)

    async def get_faction(self, faction_symbol: str) -> dict:
        """Get the information of a faction

        Args:
            faction_symbol (str): The symbol of the faction to get the information of

        Returns:
            dict: The information of the faction
        """
        return await self._get(endpoint=f"factions/{faction_symbol}")

    async def list_ships(self, limit: int = 20, page: int = 1) -> dict:
        """Get the list of ships

        Args:
            limit (int): The number of ships to get
            page (int): The page of ships to get

        Returns:
            dict: The list of ships
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the list of ships")
        params = {"limit": limit, "page": page}
        return await self._get(endpoint="my/ships", params=params)

    async def get_ship(self, ship_symbol: str) -> dict:
        """Get the information of a ship

        Args:
            ship_symbol (str): The symbol of the ship to get the information of

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the ship information")
        return await self._get(endpoint=f"ships/{ship_symbol}")

    async def purchase_ship(self, ship_type: str, waypoint_symbol: str) -> dict:
        """Purchase a ship

        Args:
            ship_type (str): The type of ship to purchase
            waypoint_symbol (str): The symbol of the waypoint to purchase the ship from

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to purchase a ship")
        data = {"type": ship_type, "location": waypoint_symbol}
        return await self._post(endpoint="my/ships", data=data)

    async def get_ship_cargo(self, ship_symbol: str) -> dict:
        """Get the cargo of a ship

        Args:
            ship_symbol (str): The symbol of the ship to get the cargo of

        Returns:
            dict: The cargo of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the ship cargo")
        return await self._get(endpoint=f"ships/{ship_symbol}/cargo")

    async def orbit_ship(self, ship_symbol: str) -> dict:
        """Orbit a ship

        Args:
            ship_symbol (str): The symbol of the ship to orbit


        Returns:
            dict: The information of the ship navigation
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to orbit a ship")
        return await self._post(endpoint=f"ships/{ship_symbol}/orbit")

    async def ship_refine(self, ship_symbol: str, data: dict) -> dict:
        """Refine a ship

        Args:
            ship_symbol (str): The symbol of the ship to refine
            data (dict): The data to send with the request, contains material to produce

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to refine a ship")
        return await self._post(endpoint=f"ships/{ship_symbol}", data=data)

    async def create_chart(self, ship_symbol: str) -> dict:
        """Create a chart

        Args:
            ship_symbol (str): The symbol of the ship to create a chart

        Returns:
            dict: The information of the chart
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to create a chart")
        return await self._post(endpoint=f"ships/{ship_symbol}/chart")

    async def get_ship_cooldown(self, ship_symbol: str) -> dict:
        """Get the cooldown of a ship

        Args:
            ship_symbol (str): The symbol of the ship to get the cooldown of

        Returns:
            dict: The cooldown of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get the ship cooldown")
        return await self._get(endpoint=f"ships/{ship_symbol}/cooldown")

    async def dock_ship(self, ship_symbol: str) -> dict:
        """Dock a ship

        Args:
            ship_symbol (str): The symbol of the ship to dock

        Returns:
            dict: The information of the ship docking
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to dock a ship")
        return await self._post(endpoint=f"ships/{ship_symbol}/dock")

    async def create_survey(self, ship_symbol: str) -> dict:
        """Create a survey

        Args:
            ship_symbol (str): The symbol of the ship to create a survey

        Returns:
            dict: The information of the survey
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to create a survey")
        return await self._post(endpoint=f"ships/{ship_symbol}/survey")

    async def extract_resources(self, ship_symbol: str, data: dict) -> dict:
        """Extract resources

        Args:
            ship_symbol (str): The symbol of the ship to extract resources
            data (dict): The data to send with the request, contains material to produce

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to extract resources")
        return await self._post(endpoint=f"ships/{ship_symbol}/extract", data=data)

    async def siphon_resources(self, ship_symbol: str) -> dict:
        """Siphon resources

        Args:
            ship_symbol (str): The symbol of the ship to siphon resources

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to siphon resources")
        return await self._post(endpoint=f"ships/{ship_symbol}/siphon")

    async def extract_resources_with_survey(
        self, ship_symbol: str, data: dict
    ) -> dict:
        """Extract resources with survey

        Args:
            ship_symbol (str): The symbol of the ship to extract resources with survey
            data (dict): The data to send with the request, contains surveey

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError(
                "You must set the API key to extract resources with survey"
            )
        return await self._post(endpoint=f"ships/{ship_symbol}/survey/extract", data=data)

    async def jettison_cargo(self, ship_symbol: str, data: dict) -> dict:
        """Jettison cargo

        Args:
            ship_symbol (str): The symbol of the ship to jettison cargo
            data (dict): The data to send with the request, contains material and quantity to jettison

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to jettison cargo")
        return await self._post(endpoint=f"ships/{ship_symbol}/jettison", data=data)

    async def jump_ship(self, ship_symbol: str, data: dict) -> dict:
        """Jump ship

        Args:
            ship_symbol (str): The symbol of the ship to jump
            data (dict): The data to send with the request, contains destination

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to jump ship")
        return await self._post(endpoint=f"ships/{ship_symbol}/jump", data=data)

    async def navigate_ship(self, ship_symbol: str, data: dict) -> dict:
        """Navigate ship

        Args:
            ship_symbol (str): The symbol of the ship to navigate
            data (dict): The data to send with the request, contains destination

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to navigate ship")
        if not data.get("waypointSymbol"):
            raise ValueError("You must set the waypointSymbol to navigate ship")
        return await self._post(endpoint=f"ships/{ship_symbol}/navigate", data=data)

    async def patch_ship_nav(self, ship_symbol: str, data: dict) -> dict:
        """Patch ship navigation

        Args:
            ship_symbol (str): The symbol of the ship to patch navigation
            data (dict): The data to send with the request, contains flight mode

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to patch ship navigation")
        if not data.get("flightMode"):
            raise ValueError("You must set the flight mode to patch ship navigation")
        return await self._patch(endpoint=f"ships/{ship_symbol}/navigate", data=data)

    async def get_ship_nav(self, ship_symbol: str) -> dict:
        """Get ship navigation

        Args:
            ship_symbol (str): The symbol of the ship to get navigation

        Returns:
            dict: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get ship navigation")
        return await self._get(endpoint=f"ships/{ship_symbol}/nav")

    async def warp_ship(self, ship_symbol: str, data: dict) -> dict:
        """

        Args:
            ship_symbol (str): The symbol of the ship to warp
            data (dict): The data to send with the request, contains waypointSymbol

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to warp ship")
        if not data.get("waypointSymbol"):
            raise ValueError("You must set the destination to warp ship")
        return await self._post(endpoint=f"ships/{ship_symbol}/warp", data=data)

    async def sell_cargo(self, ship_symbol: str, data: dict) -> dict:
        """Sell cargo

        Args:
            ship_symbol (str): The symbol of the ship to sell cargo
            data (dict): The data to send with the request, contains good and quantity

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to sell cargo")
        if not data.get("symbol") or not data.get("quantity"):
            raise ValueError("You must set the good and quantity to sell cargo")
        return await self._post(endpoint=f"ships/{ship_symbol}/sell", data=data)

    async def scan_system(self, ship_symbol: str) -> dict:
        """Scan system

        Args:
            ship_symbol (str): The symbol of the ship to scan system

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to scan system")
        if not ship_symbol:
            raise ValueError("You must set the ship symbol to scan system")
        return await self._post(endpoint=f"ships/{ship_symbol}/scan")

    async def scan_waypoints(self, ship_symbol: str) -> dict:
        """Scan waypoints

        Args:
            ship_symbol (str): The symbol of the ship to scan waypoints

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to scan waypoints")
        if not ship_symbol:
            raise ValueError("You must set the ship symbol to scan waypoints")
        return await self._post(endpoint=f"ships/{ship_symbol}/scan/waypoints")

    async def refuel_ship(self, ship_symbol: str, data: dict) -> dict:
        """Refuel ship

        Args:
            ship_symbol (str): The symbol of the ship to refuel
            data (dict): The data to send with the request, contains fuel

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to refuel ship")
        if not data.get("units") or not data.get("fromCargo"):
            raise ValueError("You must set the fuel to refuel ship")
        if type(data.get("units")) != int and type(data.get("fromCargo")) != bool:
            raise ValueError(
                "You must set units as an integer and fromCargo as a boolean"
            )
        return await self._post(endpoint=f"ships/{ship_symbol}/refuel", data=data)

    async def purchase_cargo(self, ship_symbol: str, data: dict) -> dict:
        """Purchase cargo

        Args:
            ship_symbol (str): The symbol of the ship to purchase cargo
            data (dict): The data to send with the request, contains good and quantity

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to purchase cargo")
        if not data.get("symbol") or not data.get("quantity"):
            raise ValueError("You must set the good and quantity to purchase cargo")
        return await self._post(endpoint=f"ships/{ship_symbol}/purchase", data=data)

    async def transfer_cargo(self, ship_symbol: str, data: dict) -> dict:
        """Transfer cargo

        Args:
            ship_symbol (str): The symbol of the ship to transfer cargo
            data (dict): The data to send with the request, contains good and quantity

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to transfer cargo")
        if not data.get("tradeSymbol") or not data.get("units"):
            raise ValueError("You must set the good and quantity to transfer cargo")
        return await self._post(endpoint=f"ships/{ship_symbol}/transfer", data=data)

    async def negotiate_contract(self, ship_symbol: str) -> dict:
        """Negotiate contract

        Args:
            ship_symbol (str): The symbol of the ship to negotiate contract

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to negotiate contract")
        if not ship_symbol:
            raise ValueError("You must set the ship symbol to negotiate contract")
        return await self._post(endpoint=f"ships/{ship_symbol}/negotiate")

    async def get_mounts(self, ship_symbol: str) -> dict:
        """Get mounts

        Args:
            ship_symbol (str): The symbol of the ship to get mounts

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to get mounts")
        if not ship_symbol:
            raise ValueError("You must set the ship symbol to get mounts")
        return await self._get(endpoint=f"ships/{ship_symbol}/mounts")

    async def install_mount(self, ship_symbol: str, data: dict) -> dict:
        """Install mount

        Args:
            ship_symbol (str): The symbol of the ship to install mount
            data (dict): The data to send with the request, contains mount and slot

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to install mount")
        if not data.get("symbol"):
            raise ValueError("You must set the mount to install mount")
        return await self._post(endpoint=f"ships/{ship_symbol}/mounts", data=data)

    async def remove_mount(self, ship_symbol: str, data: dict) -> dict:
        """Remove mount

        Args:
            ship_symbol (str): The symbol of the ship to remove mount
            data (dict): The data to send with the request, contains mount

        Returns:
            Coroutine: The information of the ship
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to remove mount")
        if not data.get("symbol"):
            raise ValueError("You must set the mount to remove mount")
        return await self._post(endpoint=f"ships/{ship_symbol}/mounts", data=data)

    async def list_systems(self, limit: int = 20, page: int = 1) -> dict:
        """List systems

        Args:
            limit (int): The number of systems to get
            page (int): The page of systems to get

        Returns:
            Coroutine: The list of systems
        """
        return await self._get(endpoint="systems", params={"limit": limit, "page": page})

    async def get_system(self, system_symbol: str) -> dict:
        """Get system

        Args:
            system_symbol (str): The symbol of the system to get

        Returns:
            Coroutine: The information of the system
        """
        return await self._get(endpoint=f"systems/{system_symbol}")

    async def list_waypoints_in_system(
        self,
        system_symbol: str,
        limit: int = 20,
        page: int = 1,
        traits: list[str] = [],
        type: str = "",
    ) -> dict:
        """List waypoints in system

        Args:
            system_symbol (str): The symbol of the system to get waypoints
            limit (int): The number of waypoints to get
            page (int): The page of waypoints to get

        Returns:
            Coroutine: The list of waypoints
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints",
            params={"limit": limit, "page": page, "type": type, "traits": traits},
        )

    async def get_waypoint(self, system_symbol: str, waypoint_symbol: str) -> dict:
        """Get waypoint

        Args:
            system_symbol (str): The symbol of the system to get waypoint
            waypoint_symbol (str): The symbol of the waypoint to get

        Returns:
            Coroutine: The information of the waypoint
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}"
        )

    async def get_market(self, system_symbol: str, waypoint_symbol: str) -> dict:
        """Get market

        Args:
            system_symbol (str): The symbol of the system to get market
            waypoint_symbol (str): The symbol of the waypoint to get market

        Returns:
            Coroutine: The information of the market
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}/market"
        )

    async def get_shipyard(self, system_symbol: str, waypoint_symbol: str) -> dict:
        """Get shipyard

        Args:
            system_symbol (str): The symbol of the system to get shipyard
            waypoint_symbol (str): The symbol of the waypoint to get shipyard

        Returns:
            Coroutine: The information of the shipyard
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}/shipyard"
        )

    async def get_jumpgate(self, system_symbol: str, waypoint_symbol: str) -> dict:
        """Get jumpgate

        Args:
            system_symbol (str): The symbol of the system to get jumpgate
            waypoint_symbol (str): The symbol of the waypoint to get jumpgate

        Returns:
            Coroutine: The information of the jumpgate
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}/jump-gate"
        )

    async def get_construction_site(
        self, system_symbol: str, waypoint_symbol: str
    ) -> dict:
        """Get construction site

        Args:
            system_symbol (str): The symbol of the system to get construction site
            waypoint_symbol (str): The symbol of the waypoint to get construction site

        Returns:
            Coroutine: The information of the construction site
        """
        return await self._get(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}/construction"
        )

    async def supply_construction_site(
        self, system_symbol: str, waypoint_symbol: str, data: dict
    ) -> dict:
        """Supply construction site

        Args:
            system_symbol (str): The symbol of the system to supply construction site
            waypoint_symbol (str): The symbol of the waypoint to supply construction site
            data (dict): The data to send with the request, contains good and quantity

        Returns:
            Coroutine: The information of the construction site
        """
        if not self._headers.get("Authorization"):
            raise ValueError("You must set the API key to supply construction site")
        if (
            not data.get("shipSymbol")
            or not data.get("tradeSymbol")
            or not data.get("units")
        ):
            raise ValueError(
                "You must set the ship, good and quantity to supply construction site"
            )
        return await self._post(
            endpoint=f"systems/{system_symbol}/waypoints/{waypoint_symbol}/construction/supply",
            data=data,
        )
