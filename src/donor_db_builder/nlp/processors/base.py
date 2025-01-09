from abc import ABC, abstractmethod
from typing import Any, Dict, List
import spacy
from loguru import logger


class BaseProcessor(ABC):
    "Base class for all processors"

    def __init__(self, model: str = "en_core_web_sm"):
        self.nlp = spacy.load(model)

    @abstractmethod
    def process(self, text: str) -> Dict[str, Any]:
        """Process input text and return results"""

    def __call__(self, text: str) -> Dict[str, Any]:
        try:
            return self.process(text)
        except Exception as e:
            logger.error(f"Error in processor {self.__class__.__name__}: {str(e)}")
