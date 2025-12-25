from click.testing import CliRunner
from qticonverter.cli.cli_handler import cli


def test_generate_template() -> None:
    runner = CliRunner()
    # result = runner.invoke(cli, ["generate-template", "--name","test.md","--q_type", "mcq-sa", "--folder", "."])
    result = runner.invoke(cli=cli, args=["generate-template", "--name","test.md","--q_type", "mcq-sa"])
    print(result.output)
    assert 1==result.output
