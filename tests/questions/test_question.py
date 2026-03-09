# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod

class Question(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def is_valid(self):
        """
        Docstring for is_valid
        """
        pass