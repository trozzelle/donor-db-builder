from typing import Dict, List, Any
from .base import BaseProcessor


class EntityExtractor(BaseProcessor):
    """Extracts named entities from text"""

    def __init__(self, model: str = "en_core_web_sm", entity_types: List[str] = None):
        super().__init__(model)
        self.entity_types = entity_types or ["PERSON", "ORGANIZATION"]

    def process(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        doc = self.nlp(text)
        entities = []

        for entity in doc.ents:
            if entity.label_ in self.entity_types:
                entities.append(
                    {
                        "text": entity.text,
                        "label": entity.label_,
                        "start": entity.start_char,
                        "end": entity.end_char,
                        "context": text[
                            max(0, entity.start_char - 50) : min(
                                len(text), entity.end_char + 50
                            )
                        ],
                    }
                )

        return {"entities": entities}
