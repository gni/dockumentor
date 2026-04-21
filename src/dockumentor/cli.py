import click
from dockumentor.parser import ComposeParser
from dockumentor.renderer import TemplateRenderer

@click.command()
@click.option('--compose-file', '-c', required=True, default='docker-compose.yml', help='Path to the docker-compose file.')
@click.option('--template', '-t', default='dockumentor_compose.md', help='Name of the Jinja2 template file to use.')
@click.option('--output', '-o', default='README.md', help='Path to output the generated documentation.')
@click.option('--append', '-a', is_flag=True, help='Append to existing file or replace existing Dockumentor block.')
def cli(compose_file, template, output, append):
    """Dockumentor: Auto-generate documentation from docker-compose.yml"""
    try:
        # 1. Parse into Context
        compose_context = ComposeParser.parse(compose_file)
        
        # 2. Build template payload
        template_data = TemplateRenderer.build_context_dict(compose_context)
        
        # 3. Render and save
        TemplateRenderer.render(template, output, template_data, append)
        
    except Exception as e:
        click.secho(f"Error generating documentation: {str(e)}", fg="red")
        raise click.Abort()

if __name__ == '__main__':
    cli()