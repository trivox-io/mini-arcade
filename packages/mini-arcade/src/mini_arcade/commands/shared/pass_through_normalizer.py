from __future__ import annotations


class PassThroughNormalizer:
    """
    Normalizes pass-through arguments so processors always receive ``list[str]``.
    """

    @staticmethod
    def normalize(pass_through: str | list[str]) -> list[str]:
        if not isinstance(pass_through, list):
            pass_through = [str(pass_through)]
        if pass_through and pass_through[0] == "--":
            pass_through = pass_through[1:]
        return pass_through
