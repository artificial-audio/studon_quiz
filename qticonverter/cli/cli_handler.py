"""
Presents the CLI options and handles the requests by delegating to the proper function
"""

import click

@click.group()
def cli():
    pass

# Question type abbreviations
question_type_abbr = [
    "mcq-sa",   # multiple choice (single answer)
    "mcq-ma",   # multiple choice (multiple answers)
    "num",      # numeric question
    "ess",      # essay question
    "lm",       # long menu
    "cloze",    # cloze question
    "tsq",      # text subset question
    "match",    # matching question
    "ord-v",    # ordering question (vertical)
    "ord-h"     # ordering question (horizontal)
]

@cli.command()
@click.option('--name',
              type=click.Path(exists=False,file_okay=True,dir_okay=False,writable=True),
              required=True,
              help='Output filename')
@click.option(
    "--folder",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    default = '.',
    help="Path to save the Question file"
)
@click.option('--q_type',
              type=click.Choice(choices=question_type_abbr) ,
              required=True,
              help='Type of quesiton template needed')

def generate_template(name:click.Path,folder: click.Path, q_type: click.Choice[str]):
    """Generate the template file

    Args:
        name (click.Path): Ouput file name
        folder (click.Path): _description_
        q_type (click.Choice[str]): _description_
    """
    click.echo(message=f'Template for {q_type} created at {folder} {name}')
