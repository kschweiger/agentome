from click.testing import CliRunner

from agentome.cli import bootstrap_bucket, cli


def test_cli_lists_commands() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "serve" in result.output
    assert "bootstrap-bucket" in result.output


def test_bootstrap_entrypoint_has_help() -> None:
    runner = CliRunner()

    result = runner.invoke(bootstrap_bucket, ["--help"])

    assert result.exit_code == 0
    assert "bootstrap-bucket" in result.output
