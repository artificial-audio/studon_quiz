from abc import ABC, abstractmethod
from lxml import etree

class Question(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def is_valid(self):
        """
        Docstring for is_valid
        """
        pass

    @abstractmethod
    def to_qti_xml(self, ident: str, author: str = "Bharadwaj Lakuduva Suresh Babu", ilias_version: str = "9.16.0") -> etree._Element:
        """
        Generate QTI XML item element for this question.
        
        Args:
            ident: Unique identifier for the question item
            author: Author name for metadata
            ilias_version: ILIAS version string
            
        Returns:
            An lxml etree Element representing the complete QTI item
        """
        pass