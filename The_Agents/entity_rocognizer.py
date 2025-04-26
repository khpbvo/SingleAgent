"""
Enhanced entity recognition system to replace regex-based approach.
Provides asynchronous entity extraction from text using spaCy and pattern matching.
"""
import re
import os
import asyncio
import logging
from typing import Dict, List, Set, Any, Optional, Tuple, Callable
import json
import time
from datetime import datetime
import hashlib
from functools import lru_cache

# Import spaCy singleton
from spacy_singleton import nlp_singleton

logger = logging.getLogger(__name__)

# Entity type definitions and patterns
ENTITY_TYPES = {
    "file": {
        "patterns": [
            # Common file extensions with path components
            r'([\w\/\.-]+\.(?:py|js|ts|html|css|java|cpp|h|c|rb|go|rs|php|md|json|yaml|yml|toml|xml|txt|csv|sql|sh|bat))',
            # Path-like patterns
            r'(\b(?:[a-zA-Z]:)?(?:[\\/][\w\.-]+)+\b)',
            # Common file references in technical discussions
            r'\b(requirements\.txt|package\.json|Dockerfile|\.gitignore|README\.md|setup\.py|pyproject\.toml|Cargo\.toml)\b',
        ],
        "threshold": 0.6,  # Confidence threshold
        "postprocess": lambda match: match.replace('\\', '/'),  # Normalize path separators
    },
    # [Other entity type definitions remain the same...]
}

class EntityMatch:
    """Class for storing entity match information with metadata."""
    
    def __init__(self, entity_type: str, value: str, span: Tuple[int, int], confidence: float):
        self.entity_type = entity_type
        self.value = value
        self.span = span  # Start and end positions in the text
        self.confidence = confidence
        self.metadata: Dict[str, Any] = {}
        
    def __repr__(self) -> str:
        return f"EntityMatch(type={self.entity_type}, value='{self.value}', confidence={self.confidence:.2f})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary representation."""
        return {
            "entity_type": self.entity_type,
            "value": self.value,
            "span": self.span,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

class AsyncEntityRecognizer:
    """
    Asynchronous entity extraction system that processes text to identify entities
    using both spaCy NER and regex patterns.
    """
    
    def __init__(self):
        """Initialize the entity recognizer with default patterns."""
        self.entity_types = ENTITY_TYPES
        # Compile all regex patterns for efficiency
        self._compile_patterns()
        logger.debug("AsyncEntityRecognizer initialized")
        
    def _compile_patterns(self):
        """Precompile regex patterns for faster matching."""
        for entity_type, config in self.entity_types.items():
            compiled_patterns = []
            for pattern in config["patterns"]:
                try:
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                except Exception as e:
                    logger.error(f"Error compiling pattern {pattern} for {entity_type}: {e}")
            config["compiled_patterns"] = compiled_patterns
    
    async def process_text(self, text: str) -> List[EntityMatch]:
        """
        Process text to extract entities asynchronously using both spaCy and regex.
        
        Args:
            text: Input text to process
            
        Returns:
            List of entity matches with metadata
        """
        logger.debug(f"Processing text for entities: {text[:50]}...")
        
        all_matches = []
        
        # First try to use spaCy if initialized
        try:
            if nlp_singleton.is_initialized:
                # Extract and convert spaCy entities
                entities = await nlp_singleton.extract_entities(text)
                mapped_entities = await nlp_singleton.map_entity_types(entities)
                
                # Convert to EntityMatch objects
                for entity_type, entity_list in mapped_entities.items():
                    for entity in entity_list:
                        span = (
                            entity["metadata"].get("start", 0),
                            entity["metadata"].get("end", 0)
                        )
                        match = EntityMatch(
                            entity_type=entity_type,
                            value=entity["value"],
                            span=span,
                            confidence=entity["confidence"]
                        )
                        match.metadata = entity["metadata"]
                        all_matches.append(match)
                
                logger.debug(f"Found {len(all_matches)} entities with spaCy")
        except Exception as e:
            logger.error(f"Error using spaCy for entity extraction: {e}")
        
        # Process each entity type with regex as fallback or supplement
        regex_tasks = []
        for entity_type, config in self.entity_types.items():
            task = asyncio.create_task(
                self._extract_entity_type(text, entity_type, config),
                name=f"extract_{entity_type}"
            )
            regex_tasks.append(task)
            
        # Gather regex results and merge with spaCy results
        regex_results = await asyncio.gather(*regex_tasks)
        for sublist in regex_results:
            all_matches.extend(sublist)
        
        # Remove duplicates while preserving order
        unique_matches = []
        seen = set()
        for match in all_matches:
            match_key = (match.entity_type, match.value)
            if match_key not in seen:
                seen.add(match_key)
                unique_matches.append(match)
        
        # Sort by span start position
        unique_matches.sort(key=lambda m: m.span[0])
        
        # Add entity metadata
        await self._enrich_entities(unique_matches)
        
        return unique_matches
    
    # [Rest of the class methods remain the same...]

# Public functions
@lru_cache(maxsize=10)
async def extract_entities(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Public interface to extract entities from text asynchronously.
    Uses spaCy NER when available, falling back to regex patterns.
    
    Args:
        text: Input text to process
        
    Returns:
        Dictionary of entity types with lists of entity details
    """
    # First try spaCy for entity extraction
    try:
        if nlp_singleton.is_initialized:
            # Get entities from spaCy
            spacy_entities = await nlp_singleton.extract_entities(text)
            mapped_entities = await nlp_singleton.map_entity_types(spacy_entities)
            
            # Use regex to supplement with domain-specific entities
            recognizer = AsyncEntityRecognizer()
            regex_entities = await recognizer.process_text(text)
            
            # Merge results
            merged_entities = dict(mapped_entities)  # Start with spaCy results
            
            # Add regex results
            for entity in regex_entities:
                entity_type = entity.entity_type
                if entity_type not in merged_entities:
                    merged_entities[entity_type] = []
                
                # Check if this entity is already present from spaCy
                entity_dict = entity.to_dict()
                entity_value = entity_dict["value"]
                
                # Skip if duplicate
                if entity_type in merged_entities and any(
                    e["value"] == entity_value for e in merged_entities[entity_type]
                ):
                    continue
                
                merged_entities[entity_type].append(entity_dict)
            
            return merged_entities
    except Exception as e:
        logger.error(f"Error using spaCy for entity extraction: {e}", exc_info=True)
    
    # Fallback to regex-only if spaCy fails
    recognizer = AsyncEntityRecognizer()
    entities = await recognizer.process_text(text)
    
    # Group by entity type
    grouped = {}
    for entity in entities:
        entity_type = entity.entity_type
        if entity_type not in grouped:
            grouped[entity_type] = []
        grouped[entity_type].append(entity.to_dict())
    
    return grouped

def generate_entity_id(entity_type: str, value: str) -> str:
    """Generate a unique ID for an entity."""
    return f"{entity_type}:{hashlib.md5(value.encode()).hexdigest()[:8]}"
