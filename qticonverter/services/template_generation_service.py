import click
from pathlib import Path

class TemplateGenerationService:
    def __init__(self,f_name:Path, q_type: click.Choice[str]) -> None:
        self._f_name = f_name
        self._q_type = q_type
        click.echo(f"Const called {self._f_name}")
    
    def generate_template(self):
        return True