import yaml
from typing import Any, Dict, List
from dockumentor.types import ComposeContext, ServiceNode

class ComposeParser:
    """Safely parses and normalizes docker-compose.yml files."""

    @staticmethod
    def load_yaml(filepath: str) -> Dict[str, Any]:
        """Safely loads YAML to prevent arbitrary code execution."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}

    @classmethod
    def normalize_environment(cls, env_data: Any) -> Dict[str, str]:
        """Handles both list (KEY=VAL) and dict ({KEY: VAL}) environment formats."""
        if isinstance(env_data, dict):
            return {str(k): str(v) for k, v in env_data.items()}
        if isinstance(env_data, list):
            env_dict = {}
            for item in env_data:
                if isinstance(item, str) and '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
                else:
                    env_dict[str(item)] = ""
            return env_dict
        return {}

    @classmethod
    def normalize_ports(cls, ports_data: Any, expose_data: Any) -> List[str]:
        """Handles short syntax, long syntax (dicts), and internal exposes."""
        parsed_ports = []
        
        # Handle 'ports' (External bindings)
        if isinstance(ports_data, list):
            for port in ports_data:
                if isinstance(port, dict):
                    # Docker Compose V3 Long syntax
                    target = port.get('target', '')
                    published = port.get('published', '')
                    parsed_ports.append(f"External: {published}->{target}" if published else f"External: {target}")
                else:
                    # Short syntax
                    parsed_ports.append(f"External: {port}")
                    
        # Handle 'expose' (Internal bindings)
        if isinstance(expose_data, list):
            for port in expose_data:
                parsed_ports.append(f"Internal: {port}")
                
        return parsed_ports

    @classmethod
    def normalize_depends_on(cls, depends_data: Any) -> List[str]:
        """Handles both list syntax and Compose V3 dict syntax for dependencies."""
        if isinstance(depends_data, list):
            return [str(dep) for dep in depends_data]
        if isinstance(depends_data, dict):
            return list(depends_data.keys())
        return []

    @classmethod
    def normalize_networks(cls, networks_data: Any) -> List[str]:
        """Handles network assignments."""
        if isinstance(networks_data, list):
            return [str(net) for net in networks_data]
        if isinstance(networks_data, dict):
            return list(networks_data.keys())
        return ["default"]

    @classmethod
    def parse(cls, filepath: str) -> ComposeContext:
        """Parses the file and returns a strictly typed context."""
        raw_data = cls.load_yaml(filepath)
        
        # Parse top-level networks
        global_networks = cls.normalize_networks(raw_data.get('networks', {}))
        if not raw_data.get('networks'):
            global_networks = ["default"]

        services: Dict[str, ServiceNode] = {}
        
        for name, details in raw_data.get('services', {}).items():
            if not details: 
                continue
                
            services[name] = ServiceNode(
                name=name,
                image=details.get('image', 'Built from Dockerfile'),
                ports=cls.normalize_ports(details.get('ports', []), details.get('expose', [])),
                volumes=[str(v) for v in details.get('volumes', [])] if isinstance(details.get('volumes'), list) else [],
                environment=cls.normalize_environment(details.get('environment', {})),
                depends_on=cls.normalize_depends_on(details.get('depends_on', [])),
                networks=cls.normalize_networks(details.get('networks', ["default"])),
                command=str(details.get('command', 'Default entrypoint'))
            )

        return ComposeContext(services=services, networks=global_networks)