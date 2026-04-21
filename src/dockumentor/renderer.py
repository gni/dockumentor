import os
import re
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from dockumentor.types import ComposeContext
from dockumentor.graph import MermaidBuilder

DOCKUMENTOR_START_TAG = "<!-- DOCKUMENTOR START -->"
DOCKUMENTOR_END_TAG = "<!-- DOCKUMENTOR END -->"

class TemplateRenderer:
    """Manages Jinja2 rendering and Markdown file operations."""

    @classmethod
    def build_context_dict(cls, compose_ctx: ComposeContext) -> dict:
        """Converts the typed context into a rich dictionary for Jinja2."""
        return {
            'services': compose_ctx.services,
            'networks': compose_ctx.networks,
            'mermaid_flowchart': MermaidBuilder.generate_flowchart(compose_ctx),
            'mermaid_sankey': MermaidBuilder.generate_sankey_network(compose_ctx),
            'mermaid_sequence': MermaidBuilder.generate_sequence(compose_ctx),
            'example_commands': {
                'start': 'docker compose up -d',
                'stop': 'docker compose down',
                'logs': 'docker compose logs -f [service]'
            }
        }

    @classmethod
    def render(cls, template_name: str, output_path: str, context_dict: dict, append: bool):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_name}' not found in {template_dir}")

        rendered_markdown = template.render(**context_dict)
        final_content = f"{DOCKUMENTOR_START_TAG}\n{rendered_markdown}\n{DOCKUMENTOR_END_TAG}"

        if append and os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as file:
                existing_content = file.read()

            # Bulletproof Regex Pattern: Matches everything between the START and END tags
            pattern = re.compile(rf"{re.escape(DOCKUMENTOR_START_TAG)}.*?{re.escape(DOCKUMENTOR_END_TAG)}", re.DOTALL)

            if pattern.search(existing_content):
                # We use a lambda function so regex doesn't misinterpret any '\n' inside final_content
                new_content = pattern.sub(lambda _: final_content, existing_content, count=1)
            else:
                # If tags don't exist yet, append safely to the bottom
                new_content = existing_content.rstrip() + '\n\n' + final_content
        else:
            new_content = final_content

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(new_content)
        
        print(f"✅ Documentation successfully generated at: {output_path}")