from pathlib import Path
from click.testing import CliRunner
from qticonverter.cli.cli_handler import cli
from unittest.mock import patch
import pytest

@pytest.fixture()
def create_template_file(tmp_path):
    CliRunner().invoke(cli, ["generate-template", "--name","test.md","--q_type", "mcq-sa", "--folder", str(tmp_path)])
    # Your setup code here
    yield  # Test executes here
    print("Running after test")
    # Cleanup code here

def test_generate_template_service_call() -> None:
    runner = CliRunner()
    with patch("qticonverter.cli.cli_handler.TemplateGenerationService",autospec=True) as MockClass:
        instance = MockClass.return_value
        result = runner.invoke(cli, ["generate-template", "--name","test.md","--q_type", "mcq-sa", "--folder", "."])
        MockClass.assert_called_with(f_name=Path.cwd().joinpath('test.md').resolve(),q_type='mcq-sa')
        instance.generate_template.assert_called()
        assert 0==result.exit_code

def test_generate_template(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["generate-template", "--name","test.md","--q_type", "mcq-sa", "--folder", str(tmp_path)])
    outputFile = tmp_path/'test.md'
    assert outputFile.exists()
    assert 0==result.exit_code


def test_convert_single_service_call(tmp_path: Path) -> None:
    runner = CliRunner()
    inputFile = tmp_path/'input.md'
    outputFile = tmp_path/'output.xml'
    inputFile.write_text("# Sample Question\nThis is a sample question.")
    
    with patch("qticonverter.cli.cli_handler.SingleQuestionConversionService",autospec=True) as MockClass:
        instance = MockClass.return_value
        result = runner.invoke(cli, ["convert-single", "--input", str(inputFile), "--output", str(outputFile)])
        MockClass.assert_called_with(input_file=inputFile, output_file=outputFile)
        instance.convert.assert_called()
        assert 0==result.exit_code

def test_convert_single_service_wrong_input(tmp_path: Path) -> None:
    runner = CliRunner()
    inputFile = tmp_path/'input.txt'
    outputFile = tmp_path/'output.xml'
    inputFile.write_text("This is a sample question.")
    
    result = runner.invoke(cli, ["convert-single", "--input", str(inputFile), "--output", str(outputFile)])
    assert "Input file must be a Markdown (.md) file" in result.output
    assert 1==result.exit_code

def test_convert_single_service(create_template_file, tmp_path: Path) -> None:
    runner = CliRunner()
    inputFile = tmp_path/'test.md'
    outputFile = tmp_path/'output.xml'
    
    result = runner.invoke(cli, ["convert-single", "--input", str(inputFile), "--output", str(outputFile)])
    assert outputFile.exists()
    assert 0==result.exit_code