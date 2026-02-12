"""
Mini Arcade CLI Application
"""

from __future__ import annotations

from mini_arcade.cli.cli import BaseCLIApp, CLIConfig


class MiniArcadeCLI(BaseCLIApp):
    """
    Mini Arcade CLI Application.

    :param config: CLI configuration object.
    :type config: CLIConfig
    """

    def __init__(self, config: CLIConfig):
        super().__init__(config)

        # Registry-driven commands (if you use CommandRegistry)
        self.build_commands()
