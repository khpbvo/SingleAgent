"""
Enhanced entity recognition system to replace regex-based approach.
Provides asynchronous entity extraction from text using advanced pattern matching.
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
    "url": {
        "patterns": [
            r'(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?(?:/[-\w%!.~\'*(),;:@&=+$/?#\[\]]*)?)',
            r'(www\.(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?(?:/[-\w%!.~\'*(),;:@&=+$/?#\[\]]*)?)',
            r'(github\.com/[\w-]+/[\w-]+)',
            r'((?:docs|api)\.[\w-]+\.(?:com|org|io)/(?:[\w-]+/)*(?:[\w-]+)?)',
        ],
        "threshold": 0.8,
    },
    "command": {
        "patterns": [
            r'(!|\$)([a-zA-Z0-9_\.-]+(?:\s+(?:[^\s"\']+|"[^"]*"|\'[^\']*\'))*)',
            r'\b(?:run|execute|python|pip|npm|yarn|git|docker|kubectl)\s+([a-zA-Z0-9_\.-]+(?:\s+(?:[^\s"\']+|"[^"]*"|\'[^\']*\'))*)',
            r'\b(pytest|tox|make|cargo|go|mvn)\s+([a-zA-Z0-9_\.-]+(?:\s+(?:[^\s"\']+|"[^"]*"|\'[^\']*\'))*)',
        ],
        "threshold": 0.7,
    },
    "search_query": {
        "patterns": [
            r'\b(?:search|find|look\s+for)\s+(.*?)(?:\.|$)',
            r'\bquery\s+for\s+(.*?)(?:\.|$)',
            r'\bhow\s+(?:to|do\s+I)\s+(.*?)(?:\?|\.|$)',
        ],
        "threshold": 0.6,
    },
    "task": {
        "patterns": [
            r'\b(implement|create|fix|debug|optimize|refactor)\s+([^\.]+)(?:\.|$)',
            r'\b(add|build|develop|enhance|improve)\s+([^\.]+)(?:\.|$)',
            r'\b(write|modify|update|change)\s+([^\.]+)(?:\.|$)',
        ],
        "threshold": 0.65,
    },
    "design_pattern": {
        "patterns": [
            r'\b(singleton|factory|observer|decorator|strategy|facade|adapter|composite|command|iterator|mediator|memento|proxy|visitor|state|template method|bridge|flyweight|interpreter|chain of responsibility)\b',
            r'\b(dependency injection|inversion of control|service locator|repository|unit of work|specification)\b',
        ],
        "threshold": 0.85,
    },
    "architecture_concept": {
        "patterns": [
            r'\b(module|component|service|microservice|architecture|api|rest|graphql|dependency|coupling|cohesion|solid|dry|kiss|yagni|mvc|mvvm|mvp)\b',
            r'\b(domain[- ]driven[- ]design|clean[- ]architecture|hexagonal|layered|onion|serverless|event[- ]driven|cqrs|event sourcing)\b',
        ],
        "threshold": 0.75,
    },
    "api_endpoint": {
        "patterns": [
            r'(/api/v[0-9]+/[\w/\-{}]+)',
            r'((?:GET|POST|PUT|DELETE|PATCH)\s+/[\w/\-{}]+)',
            r'(https?://[^/]+/(?:api|v[0-9])/[\w/\-{}]+)',
        ],
        "threshold": 0.8,
    },
    "programming_language": {
        "patterns": [
            r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|Scala|Perl|Haskell|Clojure|Erlang|Elixir|Dart|Julia|R|Matlab)\b',
        ],
        "threshold": 0.9,
    },
    "framework": {
        "patterns": [
            r'\b(React|Angular|Vue|Svelte|Django|Flask|FastAPI|Spring|Express|Next\.js|Ruby\s+on\s+Rails|Laravel|Symfony|ASP\.NET|Node\.js|TensorFlow|PyTorch|Pandas|NumPy|Scikit-learn)\b',
        ],
        "threshold": 0.9,
    },
    "database": {
        "patterns": [
            r'\b(PostgreSQL|MySQL|SQLite|MongoDB|Redis|Cassandra|DynamoDB|Elasticsearch|Neo4j|CouchDB|MariaDB|Oracle|SQL\s+Server|Firestore|Supabase)\b',
            r'\b(SQL|NoSQL|ACID|transaction|query|index|constraint|foreign key|primary key|database|schema)\b',
        ],
        "threshold": 0.85,
    },
    "error_message": {
        "patterns": [
            r'((?:Error|Exception|Warning|Fatal)[\s:].*)',
            r'((?:Traceback|Segmentation fault|Null pointer|undefined reference|syntax error).*)',
        ],
        "threshold": 0.75,
    },
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
    Asynchronous entity extraction system that processes text to identify:
    - files
    - URLs
    - commands
    - search queries
    - tasks
    - design patterns
    - architecture concepts
    - API endpoints
    - programming languages
    - frameworks
    - databases
    - error messages
    and more based on configurable patterns.
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
        Process text to extract entities asynchronously.
        
        Args:
            text: Input text to process
            
        Returns:
            List of entity matches with metadata
        """
        logger.debug(f"Processing text for entities: {text[:50]}...")
        
        # Process each entity type concurrently
        tasks = []
        for entity_type, config in self.entity_types.items():
            task = asyncio.create_task(
                self._extract_entity_type(text, entity_type, config),
                name=f"extract_{entity_type}"
            )
            tasks.append(task)
            
        # Gather results and flatten the list
        results = await asyncio.gather(*tasks)
        all_matches = [match for sublist in results for match in sublist]
        
        # Sort by span start position
        all_matches.sort(key=lambda m: m.span[0])
        
        # Add entity metadata
        await self._enrich_entities(all_matches)
        
        return all_matches
    
    async def _extract_entity_type(self, text: str, entity_type: str, config: Dict[str, Any]) -> List[EntityMatch]:
        """
        Extract entities of a specific type from text.
        
        Args:
            text: Input text to process
            entity_type: Type of entity to extract
            config: Configuration for this entity type
            
        Returns:
            List of entity matches
        """
        threshold = config.get("threshold", 0.5)
        matches = []
        
        # Apply each pattern
        for pattern in config.get("compiled_patterns", []):
            # Use non-blocking processing for potentially expensive regex
            matches_found = await self._process_pattern(text, pattern, entity_type, threshold, config)
            matches.extend(matches_found)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            match_key = (match.entity_type, match.value)
            if match_key not in seen:
                seen.add(match_key)
                unique_matches.append(match)
            
        return unique_matches
    
    async def _process_pattern(self, text: str, pattern, entity_type: str, threshold: float, config: Dict[str, Any]) -> List[EntityMatch]:
        """Process a single pattern on text, non-blocking."""
        try:
            # Run regex in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            pattern_matches = await loop.run_in_executor(
                None, lambda: list(pattern.finditer(text))
            )
            
            results = []
            for match in pattern_matches:
                # Determine which group to use (some patterns use capturing groups)
                if match.lastgroup:
                    # Use named group
                    value = match.group(match.lastgroup)
                    span = match.span(match.lastgroup)
                elif match.groups():
                    # Use last capturing group
                    group_index = len(match.groups())
                    value = match.group(group_index)
                    span = match.span(group_index)
                else:
                    # Use entire match
                    value = match.group(0)
                    span = match.span(0)
                
                # Skip empty matches
                if not value:
                    continue
                
                # Apply post-processing if defined
                if "postprocess" in config and callable(config["postprocess"]):
                    value = config["postprocess"](value)
                
                # Calculate initial confidence based on match length and pattern
                confidence = min(1.0, 0.5 + (len(value) / 100) + (0.2 if re.search(r'[\/\\.]', value) else 0))
                
                # Adjust confidence based on entity type and additional heuristics
                if entity_type == "file":
                    if os.path.exists(value):
                        # Existing file gets high confidence
                        confidence = max(confidence, 0.9)
                    elif re.search(r'\.(py|js|java|go|cpp|html|css|rs)$', value, re.IGNORECASE):
                        # Common code file extensions
                        confidence += 0.15
                elif entity_type == "url":
                    if re.match(r'^https?://', value):
                        # Full URLs get high confidence
                        confidence = max(confidence, 0.9)
                    elif "github.com" in value or "docs." in value:
                        # Common domains
                        confidence += 0.1
                elif entity_type == "api_endpoint":
                    if re.match(r'^/api/v[0-9]', value):
                        # Standard API pattern
                        confidence += 0.15
                elif entity_type == "programming_language" or entity_type == "framework" or entity_type == "database":
                    # These should be exact matches, so give them high confidence
                    confidence = max(confidence, 0.9)
                elif entity_type == "error_message":
                    if "exception" in value.lower() or "error:" in value.lower():
                        confidence += 0.1
                elif entity_type == "command":
                    if value.startswith("$") or value.startswith("!"):
                        confidence += 0.15
                
                # Context-based confidence boosting
                context_boost = self._get_context_confidence_boost(text, value, span, entity_type)
                confidence = min(1.0, confidence + context_boost)
                
                # Add if confidence meets threshold
                if confidence >= threshold:
                    results.append(EntityMatch(entity_type, value, span, confidence))
                    
            return results
            
        except Exception as e:
            logger.error(f"Error processing pattern for {entity_type}: {e}")
            return []
            
    def _get_context_confidence_boost(self, text: str, value: str, span: Tuple[int, int], entity_type: str) -> float:
        """
        Calculate confidence boost based on surrounding context.
        
        Args:
            text: Full text being analyzed
            value: Extracted entity value
            span: Start and end position of the match
            entity_type: Type of entity
            
        Returns:
            Confidence boost value (0.0 to 0.3)
        """
        boost = 0.0
        start, end = span
        
        # Get context before and after (up to 30 chars)
        before = text[max(0, start-30):start]
        after = text[end:min(len(text), end+30)]
        
        # Check for contextual clues based on entity type
        if entity_type == "file":
            # Words that indicate file context
            file_indicators = ["file", "path", "open", "read", "write", "save", "located at", "in the file"]
            for indicator in file_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.1
                    break
                    
        elif entity_type == "url":
            # Words that indicate URL context
            url_indicators = ["link", "website", "visit", "browse", "navigate to", "url", "site", "webpage"]
            for indicator in url_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.1
                    break
                    
        elif entity_type == "command":
            # Words that indicate command context
            cmd_indicators = ["run", "execute", "command", "terminal", "shell", "prompt", "console"]
            for indicator in cmd_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.15
                    break
        
        elif entity_type == "programming_language":
            # Words that indicate programming language context
            lang_indicators = ["code", "script", "program", "develop", "using", "in", "with"]
            for indicator in lang_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.1
                    break
                    
        elif entity_type == "framework":
            # Words that indicate framework context
            framework_indicators = ["using", "with", "framework", "library", "built with", "developed in"]
            for indicator in framework_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.1
                    break
                    
        elif entity_type == "database":
            # Words that indicate database context
            db_indicators = ["database", "store", "query", "schema", "table", "document", "collection"]
            for indicator in db_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.1
                    break
                    
        elif entity_type == "api_endpoint":
            # Words that indicate API context
            api_indicators = ["endpoint", "request", "api", "call", "route", "http", "get", "post"]
            for indicator in api_indicators:
                if indicator in before.lower() or indicator in after.lower():
                    boost += 0.15
                    break
        
        # Check for quotes which often indicate exact entities
        if ('"' in before and '"' in after) or ("'" in before and "'" in after):
            boost += 0.1
            
        return boost
    
    async def _enrich_entities(self, entities: List[EntityMatch]) -> None:
        """
        Add metadata to extracted entities asynchronously.
        
        Args:
            entities: List of entity matches to enrich
        """
        enrichment_tasks = []
        
        for entity in entities:
            task = None
            
            # Different enrichment based on entity type
            if entity.entity_type == "file" and os.path.exists(entity.value):
                task = asyncio.create_task(self._enrich_file(entity))
            elif entity.entity_type == "url":
                task = asyncio.create_task(self._enrich_url(entity))
            elif entity.entity_type == "programming_language":
                task = asyncio.create_task(self._enrich_programming_language(entity))
            elif entity.entity_type == "framework":
                task = asyncio.create_task(self._enrich_framework(entity))
            elif entity.entity_type == "database":
                task = asyncio.create_task(self._enrich_database(entity))
            elif entity.entity_type == "api_endpoint":
                task = asyncio.create_task(self._enrich_api_endpoint(entity))
                
            if task:
                enrichment_tasks.append(task)
                
        # Wait for all enrichment tasks to complete
        if enrichment_tasks:
            await asyncio.gather(*enrichment_tasks)
    
    async def _enrich_file(self, entity: EntityMatch) -> None:
        """Add file metadata to entity."""
        try:
            file_path = entity.value
            
            # Get file metadata asynchronously
            loop = asyncio.get_running_loop()
            stat_result = await loop.run_in_executor(None, os.stat, file_path)
            
            # Add file metadata
            entity.metadata = {
                "file_size": stat_result.st_size,
                "last_modified": datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                "is_directory": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1].lower(),
                "absolute_path": os.path.abspath(file_path),
            }
            
            # If file is not too large and is a text file, add preview
            if (stat_result.st_size < 10240 and 
                    not entity.metadata["is_directory"] and
                    entity.metadata["extension"] in [".py", ".txt", ".md", ".json", ".yaml", ".yml"]):
                first_lines = await loop.run_in_executor(
                    None,
                    lambda: self._read_file_preview(file_path)
                )
                entity.metadata["content_preview"] = first_lines
                
        except Exception as e:
            logger.error(f"Error enriching file entity {entity.value}: {e}")
            entity.metadata["error"] = str(e)
    
    def _read_file_preview(self, file_path: str, max_lines: int = 5) -> str:
        """Read the first few lines of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip())
                return "\n".join(lines)
        except Exception:
            return "<binary or unreadable file>"
    
    async def _enrich_url(self, entity: EntityMatch) -> None:
        """Add URL metadata to entity."""
        try:
            url = entity.value
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                elif re.match(r'^[\w\.-]+\.(com|org|io|net|dev|co)', url):
                    url = 'https://' + url
            
            # Extract domain and path
            domain_match = re.search(r'https?://([^/]+)', url)
            domain = domain_match.group(1) if domain_match else "unknown"
            
            path = ""
            if "/" in url[8:]:  # After https://
                path = "/" + url.split("/", 3)[3] if len(url.split("/", 3)) > 3 else ""
                
            entity.metadata = {
                "domain": domain,
                "path": path,
                "protocol": "https" if url.startswith("https://") else "http",
                "is_github": "github.com" in domain,
                "is_docs": any(doc_pattern in domain for doc_pattern in ["docs.", "documentation.", "api."]),
                "original_url": entity.value,
                "normalized_url": url
            }
        except Exception as e:
            logger.error(f"Error enriching URL entity {entity.value}: {e}")
            entity.metadata["error"] = str(e)
            
    @lru_cache(maxsize=100)
    def _get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a programming language."""
        languages = {
            "python": {
                "paradigm": "multi-paradigm: object-oriented, imperative, functional, procedural, structured",
                "typing": "duck, dynamic, strong",
                "extensions": [".py", ".pyi", ".pyc", ".pyd", ".pyw", ".pyx"],
                "popular_frameworks": ["Django", "Flask", "FastAPI", "Tornado", "Pyramid"],
            },
            "javascript": {
                "paradigm": "multi-paradigm: event-driven, functional, imperative, procedural, object-oriented",
                "typing": "dynamic, weak",
                "extensions": [".js", ".mjs", ".cjs"],
                "popular_frameworks": ["React", "Angular", "Vue", "Express", "Next.js"],
            },
            "typescript": {
                "paradigm": "multi-paradigm: object-oriented, imperative, functional",
                "typing": "static, strong",
                "extensions": [".ts", ".tsx"],
                "popular_frameworks": ["Angular", "React", "Next.js", "NestJS"],
            },
            "java": {
                "paradigm": "multi-paradigm: object-oriented, class-based, structured, imperative, generic, reflective, concurrent",
                "typing": "static, strong, nominal, manifest",
                "extensions": [".java", ".class", ".jar"],
                "popular_frameworks": ["Spring", "Hibernate", "Struts", "JavaServer Faces", "Micronaut"],
            },
        }
        
        # Case-insensitive lookup
        key = language.lower()
        return languages.get(key, {})
    
    async def _enrich_programming_language(self, entity: EntityMatch) -> None:
        """Add programming language metadata to entity."""
        language = entity.value.lower()
        
        # Use thread pool for CPU-bound operation
        loop = asyncio.get_running_loop()
        language_info = await loop.run_in_executor(None, self._get_language_info, language)
        
        if language_info:
            entity.metadata = language_info
        else:
            entity.metadata = {
                "detected": True,
                "normalized_name": language.lower()
            }
    
    async def _enrich_framework(self, entity: EntityMatch) -> None:
        """Add framework metadata to entity."""
        framework = entity.value.lower()
        
        # Basic framework categories
        categories = {
            "web": ["react", "angular", "vue", "svelte", "django", "flask", "fastapi", "express", "next.js", "ruby on rails", "laravel", "symfony", "asp.net"],
            "data_science": ["tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"],
            "mobile": ["react native", "flutter", "swift ui", "kotlin multiplatform", "xamarin"],
            "desktop": ["electron", "qt", "wxwidgets", "gtk"],
        }
        
        # Determine category
        framework_category = None
        for category, frameworks in categories.items():
            if any(fw in framework for fw in frameworks):
                framework_category = category
                break
                
        entity.metadata = {
            "category": framework_category or "unknown",
            "normalized_name": framework,
        }
    
    async def _enrich_database(self, entity: EntityMatch) -> None:
        """Add database metadata to entity."""
        database = entity.value.lower()
        
        # Database types
        types = {
            "relational": ["postgresql", "mysql", "sqlite", "mariadb", "oracle", "sql server"],
            "nosql_document": ["mongodb", "couchdb", "firestore"],
            "nosql_keyvalue": ["redis", "dynamodb"],
            "nosql_column": ["cassandra", "hbase"],
            "nosql_graph": ["neo4j", "tigergraph", "janusgraph"],
            "search": ["elasticsearch", "solr"],
        }
        
        # Determine type
        db_type = None
        for type_name, dbs in types.items():
            if any(db in database for db in dbs):
                db_type = type_name
                break
                
        entity.metadata = {
            "type": db_type or "unknown",
            "normalized_name": database,
            "is_sql": any(sql_db in database for sql_db in types["relational"]),
        }
    
    async def _enrich_api_endpoint(self, entity: EntityMatch) -> None:
        """Add API endpoint metadata to entity."""
        endpoint = entity.value
        
        # HTTP method detection
        http_method = None
        if endpoint.upper().startswith(("GET ", "POST ", "PUT ", "DELETE ", "PATCH ")):
            http_method, endpoint = endpoint.split(" ", 1)
        
        # Version detection
        version = None
        version_match = re.search(r'/v(\d+)/', endpoint)
        if version_match:
            version = version_match.group(1)
        
        # Parameter detection
        parameters = []
        param_matches = re.findall(r'\{([^}]+)\}', endpoint)
        if param_matches:
            parameters = param_matches
            
        entity.metadata = {
            "http_method": http_method,
            "version": version,
            "parameters": parameters,
            "is_rest": bool(re.search(r'/api/', endpoint)),
            "path_segments": [seg for seg in endpoint.split('/') if seg],
        }

@lru_cache(maxsize=10)
async def extract_entities(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Public interface to extract entities from text asynchronously.
    
    Args:
        text: Input text to process
        
    Returns:
        Dictionary of entity types with lists of entity details
    """
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