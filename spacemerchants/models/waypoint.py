from datetime import datetime

from spacetradercore.spacemerchantcore import SpaceMerchantCore


class Waypoint:
    symbol: str
    type: str
    system_symbol: str
    x: int
    y: int
    orbitals: list[str] = []
    orbits: str
    traits: list[str] = []  # TODO: define the type of the traits
    modifiers: list[str] = []  # TODO: define the type of the modifiers
    chart: dict[str, str | datetime] = {}  # TODO: define the type of the chart
    is_under_construction: bool
    _requester: SpaceMerchantCore

    @classmethod
    def from_dict(cls, requester: SpaceMerchantCore, data: dict) -> "Waypoint":
        waypoint = cls()
        waypoint._requester = requester
        waypoint.symbol = data["symbol"]
        waypoint.type = data["type"]
        waypoint.system_symbol = data["system"]
        waypoint.x = data["x"]
        waypoint.y = data["y"]
        waypoint.orbitals = data["orbitals"]
        waypoint.orbits = data.get("orbits", "")
        waypoint.traits = data.get("traits", [])
        waypoint.modifiers = data.get("modifiers", [])
        waypoint.chart = data.get("chart", {})
        waypoint.is_under_construction = data.get("isUnderConstruction", False)
        return waypoint

    def __str__(self):
        return f"Waypoint({self.symbol}, {self.type}, {self.system_symbol}, {self.x}, {self.y})"

    async def shipyard(self):
        if "SHIPYARD" not in self.traits:
            raise ValueError("This waypoint does not have a shipyard")
        return await self._requester.get_shipyard(self.system_symbol, self.symbol)

    async def purchase_ship(self, ship_type: str):
        if "SHIPYARD" not in self.traits:
            raise ValueError("This waypoint does not have a shipyard")
        pass
