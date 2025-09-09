"""SpacyModelSingleton - Asynchronous spaCy model management.

Provides a singleton access point for spaCy NLP functionality with async loading.
"""

import asyncio
import logging
from typing import Any, Optional

import spacy
from spacy.language import Language
from spacy.tokens import Doc

# ANSI color codes (defined in your main.py)
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


class SpacyModelSingleton:
    """Singleton class for spaCy NLP model.

    Ensures the model is loaded only once and provides asynchronous access.

    Usage:
        # Initialize once at application startup
        await SpacyModelSingleton.initialize()

        # Get the singleton instance
        nlp = SpacyModelSingleton()

        # Process text
        doc = await nlp.process_text("Your text here")

        # Extract entities
        entities = await nlp.extract_entities("Apple was founded by Steve Jobs in California.")
    """

    _instance = None
    _model = None
    _initialized = False
    _logger = logging.getLogger("SpacyModelSingleton")

    def __new__(cls):
        """Ensure singleton pattern - only one instance is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    async def initialize(
        cls, model_name: str = "en_core_web_sm", disable: Optional[list[str]] = None
    ) -> "SpacyModelSingleton":
        """Asynchronously initialize the spaCy model.

        Args:
            model_name: Name of the spaCy model to load (default: en_core_web_sm)
            disable: Pipeline components to disable for efficiency (e.g., ["parser", "tagger"])

        Returns:
            SpacyModelSingleton instance

        Note:
            Loading happens in a thread pool to avoid blocking the event loop

        """
        if not cls._initialized:
            cls._logger.info("Loading spaCy model %s...", model_name)
            print(f"{YELLOW}Loading spaCy model {model_name}...{RESET}")

            try:
                # Run the CPU-bound model loading in a thread pool
                loop = asyncio.get_running_loop()
                disable = disable or []

                # Use run_in_executor to load the model in a thread pool
                cls._model = await loop.run_in_executor(
                    None, lambda: spacy.load(model_name, disable=disable)
                )
                cls._initialized = True
                cls._logger.info("SpaCy model %s loaded successfully", model_name)
                print(f"{GREEN}SpaCy model {model_name} loaded successfully{RESET}")
            except Exception as e:
                cls._logger.error("Failed to load spaCy model: %s", str(e))
                print(f"{RED}Failed to load spaCy model: {str(e)}{RESET}")
                raise

        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def model(self) -> Language:
        """Get the loaded spaCy model.

        Returns:
            The spaCy Language model

        Raises:
            RuntimeError: If the model hasn't been initialized

        """
        if not self._initialized or self._model is None:
            raise RuntimeError("SpaCy model not initialized. Call initialize() first.")
        return self._model

    @property
    def is_initialized(self) -> bool:
        """Check if the model has been initialized."""
        return self._initialized

    async def process_text(self, text: str) -> Doc:
        """Process text with the spaCy NLP pipeline.

        Args:
            text: Text to process

        Returns:
            spaCy Doc object with processed annotations

        """
        # Make sure NLP is initialized
        await self._ensure_initialized()

        # Process the text using a thread executor to avoid blocking
        loop = asyncio.get_running_loop()
        doc = await loop.run_in_executor(None, self.nlp, text)
        return doc

    async def extract_entities(self, text: str) -> dict[str, list[dict[str, Any]]]:
        """Extract named entities from text using spaCy.

        Args:
            text: Text to analyze for entities

        Returns:
            Dictionary of entities grouped by type:
            {
                "PERSON": [
                    {
                        "value": "Steve Jobs",
                        "confidence": 0.95,
                        "metadata": {
                            "start": 20,
                            "end": 30,
                            "label": "PERSON"
                        }
                    }
                ],
                "ORG": [...]
            }

        """
        doc = await self.process_text(text)
        entities = {}

        # Group entities by type
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []

            # Calculate a pseudo-confidence score
            # spaCy doesn't provide confidence, so we use a fixed value
            # A more advanced implementation could use entity_ruler KB to provide real confidence
            confidence = 0.85

            entities[ent.label_].append(
                {
                    "value": ent.text,
                    "confidence": confidence,
                    "metadata": {
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "label": ent.label_,
                        "detected_at": None,  # You can add timestamp if needed
                    },
                }
            )

        return entities

    async def map_entity_types(
        self, entities: dict[str, list[dict[str, Any]]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Map spaCy entity types to your custom entity types.

        Args:
            entities: Entities extracted by spaCy, grouped by type

        Returns:
            Entities mapped to your custom entity types

        """
        # Define mapping from spaCy entity types to your custom types
        entity_mapping = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "location",
            "LOC": "location",
            "PRODUCT": "product",
            "DATE": "date",
            "TIME": "time",
            "MONEY": "money",
            "PERCENT": "percent",
            "LANGUAGE": "programming_language",  # Potential mapping
            "FAC": "building",
            "NORP": "group",
            "WORK_OF_ART": "creative_work",
        }

        mapped_entities = {}

        # Map entities to your custom types
        for spacy_type, entity_list in entities.items():
            custom_type = entity_mapping.get(spacy_type, "miscellaneous")

            if custom_type not in mapped_entities:
                mapped_entities[custom_type] = []

            mapped_entities[custom_type].extend(entity_list)

            # Update the label in metadata to the mapped type
            for entity in mapped_entities[custom_type]:
                entity["metadata"]["original_label"] = entity["metadata"]["label"]
                entity["metadata"]["label"] = custom_type

        return mapped_entities

    async def _ensure_initialized(self):
        """Ensure the model is initialized before using it.

        Raises:
            RuntimeError: If the model hasn't been initialized

        """
        if not self._initialized:
            raise RuntimeError("SpaCy model not initialized. Call initialize() first.")
        return self._model

    @property
    def nlp(self) -> Language:
        """Alias for model property for readability in client code."""
        return self.model


# Create the global singleton instance
nlp_singleton = SpacyModelSingleton()
