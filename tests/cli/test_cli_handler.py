# from click.testing import CliRunner
# from qticonverter.CLI import cli

# def test_hello_world():
#   runner = CliRunner()
#   result = runner.invoke(cli,['initdb'])
#   assert result.exit_code == 0
#   assert result.output == 'Initialized the database\n'
import click

@click.group()
def cli():
    pass

@cli.command()
def initdb():
    click.echo('Initialized the database')

@cli.command()
def dropdb():
    click.echo('Dropped the database')