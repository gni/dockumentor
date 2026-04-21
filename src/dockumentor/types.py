from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ServiceNode:
    """Internal representation of a Docker Compose Service."""
    name: str
    image: str = "No image specified"
    ports: List[str] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    command: str = "No command specified"

@dataclass
class ComposeContext:
    """Complete representation of the parsed Docker Compose file."""
    services: Dict[str, ServiceNode] = field(default_factory=dict)
    networks: List[str] = field(default_factory=list)