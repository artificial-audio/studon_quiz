"""
Presents the CLI options and handles the requests by delegating to the proper function
"""

import click
import pathlib
from ..services.template_generation_service import TemplateGenerationService
from ..services.single_question_conversion_service import SingleQuestionConversionService 

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
              type=click.Path(exists=False,file_okay=True,dir_okay=False,writable=True, path_type=pathlib.Path),
              required=True,
              help='Output filename')
@click.option(
    "--folder",
    required=True,
    type=click.Path(file_okay=False, dir_okay=True, exists=True, path_type=pathlib.Path),
    help="Path to save the Question file"
)
@click.option('--q_type',
              type=click.Choice(choices=question_type_abbr) ,
              required=True,
              help='Type of quesiton template needed')

def generate_template(name:pathlib.Path, folder: pathlib.Path, q_type: click.Choice[str]):
    """Generate the template file

    Args:
        name (click.Path): Ouput file name
        folder (click.Path): _description_
        q_type (click.Choice[str]): _description_
    """
    service = TemplateGenerationService(f_name=folder.joinpath(name).resolve(), q_type=str(q_type))
    if service.generate_template() == False:
        raise click.ClickException("Error Generating the Template")


@cli.command()
@click.option('--input',
              type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True, path_type=pathlib.Path),
              required=True,
              help='Input file to convert')
@click.option('--output',
              type=click.Path(exists=False,file_okay=True,dir_okay=False,writable=True, path_type=pathlib.Path),
              required=False,
              help='Output file to convert to')

def convert_single(input: pathlib.Path, output = pathlib.Path('.')):  
    """Convert a single file

    Args:
        input (click.Path): Input file path
        output (click.Path, optional): Output file path. Defaults to pathlib.Path('.').
    """
    if not input.suffix == '.md':
        raise click.ClickException("Input file must be a Markdown (.md) file")
        if output == pathlib.Path('.'):
            output = pathlib.Path(input.stem + '.xml')
        
    else:
        service = SingleQuestionConversionService(input_file=input, output_file=output)
        if not service.convert():
            raise click.ClickException("Error converting the file")
