# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

"""Command-line interface for QTI file conversion and template generation.

This module exposes Click-based CLI commands to convert single markdown files
or folders to QTI packages, and to generate starter markdown templates for
new questions.
"""

import click
import pathlib
from loguru import logger
import sys
from ..services.template_generation_service import TemplateGenerationService
from ..services.single_question_conversion_service import SingleQuestionConversionService 
from ..services.folder_conversion_service import FolderConversionService

def set_verbosity_level(verbose: int):
    """Configure the logging verbosity level.

    Parameters
    ----------
    verbose : int
        Verbosity level. 0=WARNING, 1=INFO, 2=DEBUG, 3+=TRACE.
    """
    # trace, debug, info, success, warning, error, critical
    logger.remove()
    if verbose == 0:
        logger.add(sink=sys.stderr, level="WARNING")
        logger.info("Verbosity set to WARNING")
    elif verbose == 1:
        logger.add(sink=sys.stderr, level="INFO")
        logger.info("Verbosity set to INFO")
        click.echo("Verbosity set to INFO")
    elif verbose == 2:
        logger.add(sink=sys.stderr, level="DEBUG")
        logger.debug("Verbosity set to DEBUG")
        click.echo("Verbosity set to DEBUG")
    else:
        logger.add(sink=sys.stderr, level="TRACE")
        logger.trace("Verbosity set to TRACE")
        click.echo("Verbosity set to TRACE")

@click.group()
def cli():
    pass

# Question type abbreviations
question_type_abbr = [
    "mcq-sa",   # multiple choice (single answer)
    "mcq-ma",   # multiple choice (multiple answers)
    "num",      # numeric question
    "text",     # free-text/essay question
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

@click.option('-v','--verbose',count=True, help='Enables verbose mode', required=False)
def generate_template(name:pathlib.Path, folder: pathlib.Path, q_type: click.Choice[str], verbose: int):
    """Generate a starter markdown template for a new question.

    Parameters
    ----------
    name : pathlib.Path
        Output file name for the template.
    folder : pathlib.Path
        Directory where the template will be created.
    q_type : str
        Question type abbreviation (e.g., mcq-sa, mcq-ma).
    verbose : int
        Verbosity level for logging.
    """
    set_verbosity_level(verbose)
    logger.info(f"Generating template: {name} in folder: {folder} for type: {q_type}")
    
    service = TemplateGenerationService(f_name=folder.joinpath(name).resolve(), q_type=str(q_type))
    if service.generate_template() == False:
        logger.error(f"Failed to generate template: {name}")
        raise click.ClickException("Error Generating the Template")
    
    logger.info(f"Successfully generated template at: {folder.joinpath(name).resolve()}")


@cli.command()
@click.option('--input',
              type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True, path_type=pathlib.Path),
              required=True,
              help='Input file to convert')
@click.option('--output',
              type=click.Path(exists=False,file_okay=True,dir_okay=False,writable=True, path_type=pathlib.Path),
              required=False,
              help='Output file to convert to')

@click.option('-v','--verbose',count=True, help='Enables verbose mode', required=False)
def convert_single(input: pathlib.Path,verbose: int, output = pathlib.Path('.') ):  
    """Convert a single markdown question file to QTI package.

    Parameters
    ----------
    input : pathlib.Path
        Path to the input markdown file.
    output : pathlib.Path, optional
        Path to the output QTI package file. Defaults to input stem + .zip.
    verbose : int
        Verbosity level for logging.
    """
    set_verbosity_level(verbose)
    logger.info(f"Starting conversion of file: {input}")
    
    if not input.suffix == '.md':
        logger.error(f"Invalid file format: {input.suffix}. Expected .md file")
        raise click.ClickException("Input file must be a Markdown (.md) file")
    
    if output == pathlib.Path('.') or output is None:
        output = pathlib.Path(input.stem + '.zip')
        logger.info(f"Output file not specified, using default: {output}")
    
    logger.info(f"Converting {input} to {output}")
    service = SingleQuestionConversionService(input_file=input, output_file=output)
    if not service.convert():
        logger.error(f"Conversion failed for file: {input}")
        raise click.ClickException("Error converting the file")
    
    logger.info(f"Successfully converted file to: {output}")


@cli.command()
@click.option('--input',
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True, path_type=pathlib.Path),
              required=True,
              help='Input folder to convert')
@click.option('--output',
              type=click.Path(exists=False,file_okay=True,dir_okay=False,writable=True, path_type=pathlib.Path),
              required=False,
              help='Output file to convert to')

@click.option('-v','--verbose',count=True, help='Enables verbose mode', required=False)
def convert_folder(input: pathlib.Path,verbose: int, output = pathlib.Path('.') ):  
    """Convert all markdown files in a folder to a single QTI package.

    Parameters
    ----------
    input : pathlib.Path
        Path to the input folder containing markdown files.
    output : pathlib.Path, optional
        Path to the output QTI package file. Defaults to folder stem + .zip.
    verbose : int
        Verbosity level for logging.
    """
    set_verbosity_level(verbose)
    logger.info(f"Starting conversion of file: {input}")
    
    
    if output == pathlib.Path('.') or output is None:
        output = pathlib.Path(input.stem + '.zip')
        logger.info(f"Output file not specified, using default: {output}")
    
    logger.info(f"Converting files in {input} to {output}")
    service = FolderConversionService(source_folder=input, output_file=output)
    if not service.convert():
        logger.error(f"Conversion failed for file: {input}")
        raise click.ClickException("Error converting the file")
    
    logger.info(f"Successfully converted files to: {output}")