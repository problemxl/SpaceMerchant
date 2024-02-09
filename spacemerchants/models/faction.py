class Faction:
    """Faction class for SpaceTrader game."""

    symbol: str
    name: str
    description: str
    headquarters: str
    traits: list[dict[str, str]]
    is_recruiting: bool

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Faction":
        """Create a Faction object from a dictionary"""
        faction = cls()
        faction.symbol = data["symbol"]
        faction.name = data["name"]
        faction.description = data["description"]
        faction.headquarters = data["headquarters"]
        faction.traits = data["traits"]
        faction.is_recruiting = data["isRecruiting"]
        return faction

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def __repr__(self):
        return f"{self.name} ({self.symbol})"
