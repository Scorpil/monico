from dataclasses import dataclass


@dataclass
class TableConfig:
    monitors: str
    tasks: str
    probes: str
