from abc import ABC, abstractmethod
from lxml import etree

class Question(ABC):
    """Abstract base class for all question types.

    Subclasses must implement validation and QTI XML generation.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def is_valid(self):
        """Validate the question instance.

        Returns:
            bool: True if the question contains all required data and is 
                ready to be converted to QTI, otherwise False.
        """
        pass

    @abstractmethod
    def to_qti_xml(self, ident: str, author: str = "User", ilias_version: str = "9.16.0") -> etree._Element:
        """Generate a QTI `item` element for this question.

        Args:
            ident: Unique identifier to use for the QTI item element.
            author: Author name to include in the QTI metadata (default provided).
            ilias_version: ILIAS version string to include in metadata.

        Returns:
            lxml.etree._Element: The top-level QTI `item` element representing 
                this question.
        """
        pass