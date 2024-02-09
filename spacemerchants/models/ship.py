from datetime import datetime

from spacetradercore.spacemerchantcore import SpaceMerchantCore


class Cargo:
    capacity: int = 0
    inventory: list = []  # TODO: define the type of the inventory
    units: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Cargo":
        cargo = cls()
        cargo.capacity = data["capacity"]
        cargo.inventory = data["inventory"]
        cargo.units = data["units"]
        return cargo


class Crew:
    capacity: int = 0
    current: int = 0
    morale: int = 0
    required: int = 0
    rotation: str = ""
    wages: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Crew":
        crew = cls()
        crew.capacity = data["capacity"]
        crew.current = data["current"]
        crew.morale = data["morale"]
        crew.required = data["required"]
        crew.rotation = data["rotation"]
        crew.wages = data["wages"]
        return crew


class Engine:
    condition: int
    description: str
    name: str
    requirements: dict[str, int]
    speed: int
    symbol: str

    @classmethod
    def from_dict(cls, data: dict) -> "Engine":
        engine = cls()
        engine.condition = data["condition"]
        engine.description = data["description"]
        engine.name = data["name"]
        engine.requirements = data["requirements"]
        engine.speed = data["speed"]
        engine.symbol = data["symbol"]
        return engine


class Frame:
    condition: int
    description: str
    name: str
    requirements: dict[str, int]
    symbol: str
    fuel_capacity: int
    module_slots: int
    mounting_points: int

    @classmethod
    def from_dict(cls, data: dict) -> "Frame":
        frame = cls()
        frame.condition = data["condition"]
        frame.description = data["description"]
        frame.name = data["name"]
        frame.requirements = data["requirements"]
        frame.symbol = data["symbol"]
        frame.fuel_capacity = data["fuelCapacity"]
        frame.module_slots = data["moduleSlots"]
        frame.mounting_points = data["mountingPoints"]
        return frame


class Fuel:
    capacity: int
    consumed: dict[str, int | datetime]
    current: int

    @classmethod
    def from_dict(cls, data: dict) -> "Fuel":
        fuel = cls()
        fuel.capacity = data["capacity"]
        fuel.consumed = data["consumed"]
        fuel.current = data["current"]
        return fuel


class Module:
    capacity: int
    description: str
    name: str
    requirements: dict[str, int]
    symbol: str

    @classmethod
    def from_dict(cls, data: dict) -> "Module":
        module = cls()
        module.capacity = data.get("capacity", 0)
        module.description = data.get("description", "")
        module.name = data.get("name", "")
        module.requirements = data.get("requirements", {})
        module.symbol = data.get("symbol", "")
        return module


class Mount:
    description: str
    name: str
    requirements: dict[str, int]
    strength: int
    symbol: str

    @classmethod
    def from_dict(cls, data: dict) -> "Mount":
        mount = cls()
        mount.description = data["description"]
        mount.name = data["name"]
        mount.requirements = data["requirements"]
        mount.strength = data["strength"]
        mount.symbol = data["symbol"]
        return mount


class Navigation:
    flight_mode: str
    arrival_time: datetime
    arrival_location: dict[str, int | str]  # TODO:
    departure_time: datetime
    departure_location: dict[str, int | str]
    status: str
    system_symbol: str
    waypoint_symbol: str

    @classmethod
    def from_dict(cls, data: dict) -> "Navigation":
        navigation = cls()
        navigation.flight_mode = data["flightMode"]
        navigation.arrival_time = datetime.fromisoformat(data["route"]["arrival"])
        navigation.arrival_location = data["route"]["origin"]["symbol"]
        navigation.departure_time = datetime.fromisoformat(
            data["route"]["departureTime"]
        )
        navigation.departure_location = data["route"]["destination"]["symbol"]
        navigation.status = data["status"]
        navigation.system_symbol = data["systemSymbol"]
        navigation.waypoint_symbol = data["waypointSymbol"]
        return navigation


class Reactor:
    condition: int
    description: str
    name: str
    power_output: int
    requirements: dict[str, int]
    symbol: str

    @classmethod
    def from_dict(cls, data: dict) -> "Reactor":
        reactor = cls()
        reactor.condition = data["condition"]
        reactor.description = data["description"]
        reactor.name = data["name"]
        reactor.power_output = data["powerOutput"]
        reactor.requirements = data["requirements"]
        reactor.symbol = data["symbol"]
        return reactor


class Ship:
    cargo: Cargo
    crew: Crew
    engine: Engine
    frame: Frame
    fuel: Fuel
    modules: list[Module]
    mounts: list[Mount]
    navigation: Navigation
    reactor: Reactor
    faction: str
    name: str
    role: str
    symbol: str
    _requester: SpaceMerchantCore

    # create a ship object from a dictionary
    @classmethod
    def from_dict(cls, requester:SpaceMerchantCore, data: dict) -> "Ship":
        ship = cls()
        ship._requester = requester
        cargo_data = data["cargo"]
        crew_data = data["crew"]
        engine_data = data["engine"]
        frame_data = data["frame"]
        fuel_data = data["fuel"]
        navigation_data = data["nav"]
        reactor_data = data["reactor"]

        ship.cargo = Cargo.from_dict(cargo_data)
        ship.crew = Crew.from_dict(crew_data)
        ship.engine = Engine.from_dict(engine_data)
        ship.frame = Frame.from_dict(frame_data)
        ship.fuel = Fuel.from_dict(fuel_data)
        ship.navigation = Navigation.from_dict(navigation_data)
        ship.reactor = Reactor.from_dict(reactor_data)

        ship.modules = [Module.from_dict(module) for module in data["modules"]]
        ship.mounts = [Mount.from_dict(mount) for mount in data["mounts"]]
        ship.faction = data["registration"]["factionSymbol"]
        ship.name = data["registration"]["name"]
        ship.role = data["registration"]["role"]
        ship.symbol = data["symbol"]

        return ship

    async def navigate(self, waypoint: str) -> Navigation:
        """Navigate to a waypoint"""
        if self.navigation.status == "DOCKED":  # TODO: define the status
            raise ValueError("The ship is currently docked and cannot navigate")
        
        flight_plan = await self._requester.navigate_ship(self.symbol, {"waypointSymbol": waypoint})
        self.navigation = Navigation.from_dict(flight_plan.get("nav", {}))
        return self.navigation

    def __str__(self):
        return f"{self.name} ({self.role})"

    def __repr__(self):
        return f"{self.name} ({self.role})"
