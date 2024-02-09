from loguru import logger
from spacemerchants.models.faction import Faction
from spacemerchants.models.waypoint import Waypoint
from spacetradercore.spacemerchantcore import SpaceMerchantCore


class System:
    symbol: str
    sector_symbol: str
    type: str
    x: int
    y: int
    factions: list[Faction] = []
    _waypoints: list[Waypoint]  # TODO: define the type of the waypoints
    _requester: SpaceMerchantCore

    @classmethod
    def from_dict(cls, requester: SpaceMerchantCore, data: dict) -> "System":
        system = cls()
        system._requester = requester
        system.symbol = data["symbol"]
        system.sector_symbol = data["sectorSymbol"]
        system.type = data["type"]
        system.x = data["x"]
        system.y = data["y"]
        system_dict = {"system": system.symbol}
        waypoints = [{**waypoint, **system_dict} for waypoint in data.get("waypoints", [])]
        system._waypoints = [Waypoint.from_dict(requester, waypoint) for waypoint in waypoints]
        system.factions = [
            Faction.from_dict(faction) for faction in data.get("factions", [])
        ]
        return system

    async def waypoints(self, force: bool = False) -> list[Waypoint]:
        """Get the waypoints for the system"""
        if not force and self._waypoints:
            return self._waypoints

        limit = 20
        page = 1
        while True:
            response = await self._requester.list_waypoints_in_system(
                self.symbol, limit=limit, page=page
            )
            waypoints = response.get("data", [])
            meta = response.get("meta", {})
            self._waypoints.extend([Waypoint.from_dict(self._requester, waypoint) for waypoint in waypoints])
            if meta.get("total") == len(self._waypoints):
                break
            page += 1
        return self._waypoints

    async def shipyard(self) -> list[dict]:
        """Get the shipyard for the system"""
        limit = 20
        page = 1
        shipyards = []
        while True:
            response = await self._requester.list_waypoints_in_system(
                self.symbol, limit=limit, page=page, traits=["SHIPYARD"]
            )
            logger.debug(f"System | shipyard | {response =:}")
            ships = response.get("data", [])
            meta = response.get("meta", {})
            shipyards.extend(ships)
            if meta.get("total") == len(ships):
                break
            page += 1
        return shipyards

    @classmethod
    async def get(cls, requester: SpaceMerchantCore, symbol: str) -> "System":
        """Get the details of a system"""
        response = await requester.get_system(symbol)
        return cls.from_dict(requester, response.get("data", {}))
    
    def __str__(self):
        return f"System({self.symbol}, {self.sector_symbol}, {self.type}, {self.x}, {self.y})"