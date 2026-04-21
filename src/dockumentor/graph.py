import re
from typing import Dict, List, Set
from dockumentor.types import ComposeContext, ServiceNode

class MermaidBuilder:
    """Builder pattern for constructing clean, structured Mermaid diagrams."""

    @staticmethod
    def sanitize_id(text: str) -> str:
        """Sanitize strings for valid Mermaid element IDs."""
        text = text.replace(r"\|", "_").replace("-", "_").replace(".", "_")
        return re.sub(r'[^a-zA-Z0-9_]', '', text)

    @classmethod
    def _get_reduced_dependencies(cls, context: ComposeContext) -> Dict[str, Set[str]]:
        """
        Applies Transitive Reduction to eliminate redundant dependency lines (spaghetti).
        If A->B and B->C, the redundant A->C line is removed for visual clarity.
        """
        graph = {name: set(svc.depends_on) for name, svc in context.services.items()}
        graph = {u: {v for v in deps if v in context.services} for u, deps in graph.items()}
        
        reduced = {u: set(v) for u, v in graph.items()}
        
        for u in graph:
            for v in graph[u]:
                stack = [v]
                visited = set()
                while stack:
                    curr = stack.pop()
                    if curr in visited:
                        continue
                    visited.add(curr)
                    if curr != v:
                        reduced[u].discard(curr)
                    stack.extend(graph.get(curr, []))
                    
        return reduced

    @classmethod
    def generate_flowchart(cls, context: ComposeContext) -> str:
        """
        Generates a Top-Down architecture diagram using the ELK renderer for 
        superior edge routing, styled nodes, and transitive reduction.
        """
        lines: List[str] = [
            "%%{init: {\"flowchart\": {\"defaultRenderer\": \"elk\", \"nodeSpacing\": 40, \"rankSpacing\": 50}}}%%",
            "flowchart TD",
            "    classDef exposed fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff,rx:5px,ry:5px;",
            "    classDef internal fill:#1a202c,stroke:#718096,stroke-width:1px,color:#e2e8f0,rx:5px,ry:5px;",
            "    classDef datastore fill:#2b6cb0,stroke:#63b3ed,stroke-width:2px,color:#fff,rx:8px,ry:8px;"
        ]
        
        datastores = {"postgres", "mysql", "redis", "mongo", "db", "mariadb", "elasticsearch", "rabbitmq"}
        reduced_deps = cls._get_reduced_dependencies(context)
        
        for name, service in context.services.items():
            safe_name = cls.sanitize_id(name)
            img_short = service.image.split('/')[-1]
            is_ds = any(ds in name.lower() or ds in img_short.lower() for ds in datastores)
            
            if service.ports:
                ports_str = "<br/>🔌 " + " | ".join(p.replace("External: ", "") for p in service.ports if "External" in p)
                label = f"<b>{name}</b><br/><i>{img_short}</i>{ports_str}"
                lines.append(f"    {safe_name}([\"{label}\"]):::exposed")
            elif is_ds:
                label = f"<b>{name}</b><br/><i>{img_short}</i><br/>💾 Datastore"
                lines.append(f"    {safe_name}[(\"{label}\")]:::datastore")
            else:
                label = f"<b>{name}</b><br/><i>{img_short}</i>"
                lines.append(f"    {safe_name}[\"{label}\"]:::internal")
            
        for name, deps in reduced_deps.items():
            safe_name = cls.sanitize_id(name)
            for dep in deps:
                safe_dep = cls.sanitize_id(dep)
                lines.append(f"    {safe_name} --> {safe_dep}")

        return "\n".join(lines)

    @classmethod
    def generate_sankey_network(cls, context: ComposeContext) -> str:
        connections: Set[str] = set()
        for name, service in context.services.items():
            safe_name = cls.sanitize_id(name)
            if service.ports:
                for port in service.ports:
                    source = "Internal Scope" if "Internal" in port else "External Scope"
                    connections.add(f"{source}, {safe_name}, 1")
            elif service.networks:
                for net in service.networks:
                    connections.add(f"Net: {net}, {safe_name}, 1")
            else:
                connections.add(f"Isolated, {safe_name}, 1")

        if not connections:
            return ""
            
        lines = ["sankey-beta"]
        lines.extend([f"    {conn}" for conn in sorted(connections)])
        return "\n".join(lines)

    @classmethod
    def generate_sequence(cls, context: ComposeContext) -> str:
        lines: List[str] = ["sequenceDiagram", "    autonumber"]
        for name, service in context.services.items():
            safe_name = cls.sanitize_id(name)
            lines.append(f"    participant {safe_name} as {name}")
            
        for name, service in context.services.items():
            safe_name = cls.sanitize_id(name)
            for dependency in service.depends_on:
                if dependency in context.services:
                    safe_dep = cls.sanitize_id(dependency)
                    lines.append(f"    {safe_name}->>{safe_dep}: Connection / Init")
                
        return "\n".join(lines)