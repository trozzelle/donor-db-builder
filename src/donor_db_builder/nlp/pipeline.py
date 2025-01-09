from typing import List, Dict, Any
from .base import BaseProcessor
from loguru import logger


class NLPPipeline(BaseProcessor):
    """Orchestrates the NLP processing pipeline"""

    def __init__(self, processors: List[BaseProcessor]):
        self.processors = processors

    def process(self, text: str) -> Dict[str, Any]:
        """Run text through all processors in sequence"""

        results = {}

        for processor in self.processors:
            try:
                processor_result = processor(text)
                results.update(processor_result)
            except Exception as e:
                logger.error(f"Error processing {processor.__class__.__name__}: {e}")
                raise

        return results
