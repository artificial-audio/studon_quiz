from click.testing import CliRunner
from qticonverter.cli.cli_handler import cli
from unittest.mock import patch
from pathlib import Path

def test_generate_template() -> None:
    runner = CliRunner()
    with patch("qticonverter.cli.cli_handler.TemplateGenerationService",autospec=True) as MockClass:
        instance = MockClass.return_value
        result = runner.invoke(cli, ["generate-template", "--name","test.md","--q_type", "mcq-sa", "--folder", "."])
        MockClass.assert_called_with(f_name=Path.cwd().joinpath('test.md').resolve(),q_type='mcq-sa')
        instance.generate_template.assert_called()
        assert 0==result.exit_code
