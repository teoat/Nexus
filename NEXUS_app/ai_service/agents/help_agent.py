#!/usr/bin/env python3
"""
Help Agent RAG System - Interactive Guidance and Knowledge Management

This module implements the HelpAgent class that provides
comprehensive help and guidance capabilities for the forensic platform.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class HelpCategory(Enum):
    """Categories of help content."""

    GETTING_STARTED = "getting_started"  # Platform introduction
    USER_GUIDE = "user_guide"  # User manual and guides
    TROUBLESHOOTING = "troubleshooting"  # Problem solving
    BEST_PRACTICES = "best_practices"  # Recommended practices
    API_REFERENCE = "api_reference"  # API documentation
    WORKFLOW_GUIDES = "workflow_guides"  # Process workflows
    SECURITY = "security"  # Security guidelines
    COMPLIANCE = "compliance"  # Compliance information
    CUSTOM = "custom"  # Custom help content


class ContentType(Enum):
    """Types of help content."""

    TEXT = "text"  # Plain text content
    MARKDOWN = "markdown"  # Markdown formatted
    HTML = "html"  # HTML content
    VIDEO = "video"  # Video tutorials
    INTERACTIVE = "interactive"  # Interactive guides
    FAQ = "faq"  # Frequently asked questions
    TUTORIAL = "tutorial"  # Step-by-step tutorials
    REFERENCE = "reference"  # Reference material


class SearchType(Enum):
    """Types of search operations."""

    KEYWORD = "keyword"  # Keyword-based search
    SEMANTIC = "semantic"  # Semantic search
    FUZZY = "fuzzy"  # Fuzzy matching
    CATEGORY = "category"  # Category-based search
    TAG = "tag"  # Tag-based search
    CONTEXT = "context"  # Context-aware search


@dataclass
class HelpContent:
    """A piece of help content."""

    content_id: str
    title: str
    content: str
    content_type: ContentType
    category: HelpCategory
    tags: List[str]
    author: str
    creation_date: datetime
    last_updated: datetime
    version: str
    language: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Result of a help search."""

    result_id: str
    content_id: str
    title: str
    snippet: str
    relevance_score: float
    category: HelpCategory
    content_type: ContentType
    tags: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserQuery:
    """A user query for help."""

    query_id: str
    user_id: str
    query_text: str
    search_type: SearchType
    context: Dict[str, Any]
    timestamp: datetime
    results_returned: int
    user_feedback: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractiveGuide:
    """An interactive help guide."""

    guide_id: str
    title: str
    description: str
    steps: List[Dict[str, Any]]
    current_step: int
    user_progress: Dict[str, Any]
    completion_status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HelpMetrics:
    """Metrics for help system performance."""

    total_content_items: int
    total_queries: int
    successful_searches: int
    average_response_time: float
    user_satisfaction: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class HelpAgent:
    """
    Comprehensive help and guidance system.

    The HelpAgent is responsible for:
    - Managing help content and knowledge base
    - Providing intelligent search and retrieval
    - Supporting interactive guidance and tutorials
    - Managing user queries and feedback
    - Supporting multiple languages and content types
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the HelpAgent."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_semantic_search = config.get("enable_semantic_search", True)
        self.enable_fuzzy_search = config.get("enable_fuzzy_search", True)
        self.max_search_results = config.get("max_search_results", 20)
        self.supported_languages = config.get(
            "supported_languages", ["en", "es", "fr", "de"]
        )

        # Content management
        self.help_content: Dict[str, HelpContent] = {}
        self.content_index: Dict[str, List[str]] = defaultdict(list)
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.category_index: Dict[HelpCategory, List[str]] = defaultdict(list)

        # Search and retrieval
        self.search_history: Dict[str, List[str]] = defaultdict(list)
        self.user_queries: Dict[str, UserQuery] = {}
        self.query_feedback: Dict[str, List[str]] = defaultdict(list)

        # Interactive guides
        self.interactive_guides: Dict[str, InteractiveGuide] = {}
        self.user_progress: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Performance tracking
        self.total_content_items = 0
        self.total_queries = 0
        self.successful_searches = 0
        self.total_response_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize help agent components
        self._initialize_help_agent_components()

        self.logger.info("HelpAgent initialized successfully")

    async def start(self):
        """Start the HelpAgent."""
        self.logger.info("Starting HelpAgent...")

        # Initialize help agent components
        await self._initialize_help_agent_components()

        # Start background tasks
        asyncio.create_task(self._update_content_index())
        asyncio.create_task(self._analyze_user_feedback())

        self.logger.info("HelpAgent started successfully")

    async def stop(self):
        """Stop the HelpAgent."""
        self.logger.info("Stopping HelpAgent...")
        self.logger.info("HelpAgent stopped")

    def _initialize_help_agent_components(self):
        """Initialize help agent components."""
        try:
            # Initialize help content
            self._initialize_help_content()

            # Initialize search components
            self._initialize_search_components()

            # Initialize interactive guides
            self._initialize_interactive_guides()

            self.logger.info("Help agent components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing help agent components: {e}")

    def _initialize_help_content(self):
        """Initialize help content."""
        try:
            # Getting started content
            getting_started_content = HelpContent(
                content_id=str(uuid.uuid4()),
                title="Welcome to the Nexus Platform",
                content="""
# Welcome to the Nexus Platform

This platform provides comprehensive forensic analysis capabilities including:

## Key Features
- **Reconciliation Agent**: Automated Nexus
- **Fraud Detection**: Advanced fraud detection algorithms
- **Risk Assessment**: Multi-factor risk analysis
- **Evidence Processing**: Comprehensive evidence management
- **Multi-Agent Orchestration**: Coordinated analysis workflows

## Getting Started
1. **Authentication**: Log in with your credentials
2. **Case Creation**: Create a new forensic case
3. **Data Upload**: Upload evidence and data files
4. **Analysis**: Run automated analysis workflows
5. **Review Results**: Examine analysis results and reports

## Support
For additional help, use the search function or browse our knowledge base.
                """,
                content_type=ContentType.MARKDOWN,
                category=HelpCategory.GETTING_STARTED,
                tags=["introduction", "platform", "features", "getting-started"],
                author="System",
                creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version="1.0",
                language="en",
            )

            # User guide content
            user_guide_content = HelpContent(
                content_id=str(uuid.uuid4()),
                title="User Guide - Complete Platform Manual",
                content="""
# User Guide - Complete Platform Manual

## Table of Contents
1. [Authentication & Security](#authentication)
2. [Case Management](#case-management)
3. [Evidence Processing](#evidence-processing)
4. [Analysis Workflows](#analysis-workflows)
5. [Reporting & Export](#reporting)

## Authentication & Security
The platform uses JWT-based authentication with role-based access control.

## Case Management
Create, manage, and track forensic cases through their lifecycle.

## Evidence Processing
Upload, process, and analyze various types of evidence.

## Analysis Workflows
Run automated analysis workflows using AI agents.

## Reporting & Export
Generate comprehensive reports and export results.
                """,
                content_type=ContentType.MARKDOWN,
                category=HelpCategory.USER_GUIDE,
                tags=["user-guide", "manual", "documentation", "tutorials"],
                author="System",
                creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version="1.0",
                language="en",
            )

            # Troubleshooting content
            troubleshooting_content = HelpContent(
                content_id=str(uuid.uuid4()),
                title="Troubleshooting Common Issues",
                content="""
# Troubleshooting Common Issues

## Authentication Problems
- **Issue**: Cannot log in
- **Solution**: Check credentials and contact administrator

## File Upload Issues
- **Issue**: Files not uploading
- **Solution**: Check file size and format requirements

## Analysis Failures
- **Issue**: Analysis workflows failing
- **Solution**: Verify data quality and system resources

## Performance Issues
- **Issue**: Slow response times
- **Solution**: Check system resources and network connectivity
                """,
                content_type=ContentType.MARKDOWN,
                category=HelpCategory.TROUBLESHOOTING,
                tags=["troubleshooting", "problems", "solutions", "help"],
                author="System",
                creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version="1.0",
                language="en",
            )

            # Store content
            self.help_content[getting_started_content.content_id] = (
                getting_started_content
            )
            self.help_content[user_guide_content.content_id] = user_guide_content
            self.help_content[troubleshooting_content.content_id] = (
                troubleshooting_content
            )

            # Index content
            self._index_content(getting_started_content)
            self._index_content(user_guide_content)
            self._index_content(troubleshooting_content)

            # Update metrics
            self.total_content_items = len(self.help_content)

            self.logger.info(f"Initialized {len(self.help_content)} help content items")

        except Exception as e:
            self.logger.error(f"Error initializing help content: {e}")

    def _index_content(self, content: HelpContent):
        """Index help content for search."""
        try:
            # Index by category
            self.category_index[content.category].append(content.content_id)

            # Index by tags
            for tag in content.tags:
                self.tag_index[tag.lower()].append(content.content_id)

            # Index by language
            self.content_index[content.language].append(content.content_id)

            # Index by content type
            self.content_index[content.content_type.value].append(content.content_id)

        except Exception as e:
            self.logger.error(f"Error indexing content: {e}")

    def _initialize_search_components(self):
        """Initialize search components."""
        try:
            # Initialize search algorithms
            self.search_algorithms = {
                SearchType.KEYWORD: self._keyword_search,
                SearchType.SEMANTIC: self._semantic_search,
                SearchType.FUZZY: self._fuzzy_search,
                SearchType.CATEGORY: self._category_search,
                SearchType.TAG: self._tag_search,
                SearchType.CONTEXT: self._context_search,
            }

            self.logger.info("Search components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing search components: {e}")

    def _initialize_interactive_guides(self):
        """Initialize interactive guides."""
        try:
            # Platform tour guide
            tour_guide = InteractiveGuide(
                guide_id=str(uuid.uuid4()),
                title="Platform Tour Guide",
                description="Interactive tour of the forensic platform features",
                steps=[
                    {
                        "step_number": 1,
                        "title": "Welcome",
                        "description": "Welcome to the forensic platform",
                        "action": "show_welcome",
                        "duration": 30,
                    },
                    {
                        "step_number": 2,
                        "title": "Dashboard Overview",
                        "description": "Explore the main dashboard",
                        "action": "highlight_dashboard",
                        "duration": 45,
                    },
                    {
                        "step_number": 3,
                        "title": "Case Creation",
                        "description": "Learn how to create a new case",
                        "action": "show_case_creation",
                        "duration": 60,
                    },
                    {
                        "step_number": 4,
                        "title": "Evidence Upload",
                        "description": "Upload and process evidence",
                        "action": "show_evidence_upload",
                        "duration": 60,
                    },
                    {
                        "step_number": 5,
                        "title": "Analysis Workflows",
                        "description": "Run automated analysis",
                        "action": "show_analysis_workflows",
                        "duration": 90,
                    },
                ],
                current_step=0,
                user_progress={},
                completion_status="not_started",
            )

            # Store guide
            self.interactive_guides[tour_guide.guide_id] = tour_guide

            self.logger.info(
                f"Initialized {len(self.interactive_guides)} interactive guides"
            )

        except Exception as e:
            self.logger.error(f"Error initializing interactive guides: {e}")

    async def search_help(
        self,
        query_text: str,
        user_id: str,
        search_type: SearchType = SearchType.KEYWORD,
        context: Dict[str, Any] = None,
        max_results: int = None,
    ) -> List[SearchResult]:
        """Search for help content."""
        try:
            start_time = time.time()

            if max_results is None:
                max_results = self.max_search_results

            # Create user query
            query = UserQuery(
                query_id=str(uuid.uuid4()),
                user_id=user_id,
                query_text=query_text,
                search_type=search_type,
                context=context or {},
                timestamp=datetime.utcnow(),
                results_returned=0,
                user_feedback=None,
            )

            # Store query
            self.user_queries[query.query_id] = query

            # Perform search based on type
            if search_type in self.search_algorithms:
                search_function = self.search_algorithms[search_type]
                results = await search_function(query_text, context, max_results)
            else:
                # Default to keyword search
                results = await self._keyword_search(query_text, context, max_results)

            # Update query with results
            query.results_returned = len(results)

            # Store search history
            self.search_history[user_id].append(query.query_id)

            # Update metrics
            self.total_queries += 1
            self.successful_searches += 1
            response_time = time.time() - start_time
            self.total_response_time += response_time

            self.logger.info(
                f"Search completed for user {user_id} in {response_time:.2f}s"
            )

            return results

        except Exception as e:
            self.logger.error(f"Error searching help: {e}")
            return []

    async def _keyword_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform keyword-based search."""
        try:
            results = []
            query_lower = query_text.lower()

            for content_id, content in self.help_content.items():
                # Check title
                title_score = self._calculate_keyword_score(
                    query_lower, content.title.lower()
                )

                # Check content
                content_score = self._calculate_keyword_score(
                    query_lower, content.content.lower()
                )

                # Check tags
                tag_score = self._calculate_tag_score(query_lower, content.tags)

                # Calculate total score
                total_score = (
                    (title_score * 0.4) + (content_score * 0.4) + (tag_score * 0.2)
                )

                if total_score > 0:
                    # Create snippet
                    snippet = self._create_content_snippet(content.content, query_lower)

                    result = SearchResult(
                        result_id=str(uuid.uuid4()),
                        content_id=content_id,
                        title=content.title,
                        snippet=snippet,
                        relevance_score=total_score,
                        category=content.category,
                        content_type=content.content_type,
                        tags=content.tags,
                    )

                    results.append(result)

            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results[:max_results]

        except Exception as e:
            self.logger.error(f"Error in keyword search: {e}")
            return []

    def _calculate_keyword_score(self, query: str, text: str) -> float:
        """Calculate keyword relevance score."""
        try:
            query_words = query.split()
            text_words = text.split()

            if not query_words or not text_words:
                return 0.0

            matches = 0
            for query_word in query_words:
                if len(query_word) > 2:  # Skip very short words
                    for text_word in text_words:
                        if query_word in text_word or text_word in query_word:
                            matches += 1
                            break

            return matches / len(query_words)

        except Exception as e:
            self.logger.error(f"Error calculating keyword score: {e}")
            return 0.0

    def _calculate_tag_score(self, query: str, tags: List[str]) -> float:
        """Calculate tag relevance score."""
        try:
            if not tags:
                return 0.0

            query_words = query.split()
            tag_matches = 0

            for tag in tags:
                tag_lower = tag.lower()
                for query_word in query_words:
                    if query_word in tag_lower or tag_lower in query_word:
                        tag_matches += 1
                        break

            return tag_matches / len(tags)

        except Exception as e:
            self.logger.error(f"Error calculating tag score: {e}")
            return 0.0

    def _create_content_snippet(
        self, content: str, query: str, max_length: int = 200
    ) -> str:
        """Create a content snippet highlighting the query."""
        try:
            # Find query position in content
            content_lower = content.lower()
            query_lower = query.lower()

            pos = content_lower.find(query_lower)
            if pos == -1:
                # Query not found, return beginning of content
                return (
                    content[:max_length] + "..."
                    if len(content) > max_length
                    else content
                )

            # Create snippet around query
            start = max(0, pos - max_length // 2)
            end = min(len(content), pos + max_length // 2)

            snippet = content[start:end]

            # Add ellipsis if needed
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."

            return snippet

        except Exception as e:
            self.logger.error(f"Error creating content snippet: {e}")
            return (
                content[:max_length] + "..." if len(content) > max_length else content
            )

    async def _semantic_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform semantic search (placeholder for advanced implementation)."""
        try:
            # For now, fall back to keyword search
            # In a full implementation, this would use embeddings or semantic models
            return await self._keyword_search(query_text, context, max_results)

        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []

    async def _fuzzy_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform fuzzy search."""
        try:
            results = []
            query_lower = query_text.lower()

            for content_id, content in self.help_content.items():
                # Calculate fuzzy match score
                title_score = self._calculate_fuzzy_score(
                    query_lower, content.title.lower()
                )
                content_score = self._calculate_fuzzy_score(
                    query_lower, content.content.lower()
                )

                # Use the higher score
                total_score = max(title_score, content_score)

                if total_score > 0.3:  # Fuzzy threshold
                    snippet = self._create_content_snippet(content.content, query_lower)

                    result = SearchResult(
                        result_id=str(uuid.uuid4()),
                        content_id=content_id,
                        title=content.title,
                        snippet=snippet,
                        relevance_score=total_score,
                        category=content.category,
                        content_type=content.content_type,
                        tags=content.tags,
                    )

                    results.append(result)

            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results[:max_results]

        except Exception as e:
            self.logger.error(f"Error in fuzzy search: {e}")
            return []

    def _calculate_fuzzy_score(self, query: str, text: str) -> float:
        """Calculate fuzzy match score."""
        try:
            # Simple fuzzy matching based on character similarity
            if not query or not text:
                return 0.0

            # Calculate character overlap
            query_chars = set(query)
            text_chars = set(text)

            intersection = len(query_chars.intersection(text_chars))
            union = len(query_chars.union(text_chars))

            if union == 0:
                return 0.0

            return intersection / union

        except Exception as e:
            self.logger.error(f"Error calculating fuzzy score: {e}")
            return 0.0

    async def _category_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform category-based search."""
        try:
            results = []

            # Extract category from context or query
            target_category = context.get("category")
            if not target_category:
                # Try to infer category from query
                target_category = self._infer_category_from_query(query_text)

            if target_category and target_category in self.category_index:
                content_ids = self.category_index[target_category]

                for content_id in content_ids[:max_results]:
                    content = self.help_content.get(content_id)
                    if content:
                        snippet = self._create_content_snippet(
                            content.content, query_text.lower()
                        )

                        result = SearchResult(
                            result_id=str(uuid.uuid4()),
                            content_id=content_id,
                            title=content.title,
                            snippet=snippet,
                            relevance_score=0.8,  # High score for category match
                            category=content.category,
                            content_type=content.content_type,
                            tags=content.tags,
                        )

                        results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in category search: {e}")
            return []

    def _infer_category_from_query(self, query: str) -> Optional[HelpCategory]:
        """Infer help category from query text."""
        try:
            query_lower = query.lower()

            # Category keywords
            category_keywords = {
                HelpCategory.GETTING_STARTED: [
                    "start",
                    "begin",
                    "welcome",
                    "introduction",
                    "first",
                ],
                HelpCategory.USER_GUIDE: [
                    "guide",
                    "manual",
                    "how to",
                    "tutorial",
                    "instructions",
                ],
                HelpCategory.TROUBLESHOOTING: [
                    "problem",
                    "error",
                    "issue",
                    "fix",
                    "solve",
                    "help",
                ],
                HelpCategory.BEST_PRACTICES: [
                    "best",
                    "practice",
                    "recommend",
                    "should",
                    "advice",
                ],
                HelpCategory.API_REFERENCE: [
                    "api",
                    "endpoint",
                    "request",
                    "response",
                    "code",
                ],
                HelpCategory.WORKFLOW_GUIDES: [
                    "workflow",
                    "process",
                    "step",
                    "procedure",
                ],
                HelpCategory.SECURITY: [
                    "security",
                    "authentication",
                    "authorization",
                    "permission",
                ],
                HelpCategory.COMPLIANCE: [
                    "compliance",
                    "regulation",
                    "policy",
                    "standard",
                ],
            }

            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        return category

            return None

        except Exception as e:
            self.logger.error(f"Error inferring category: {e}")
            return None

    async def _tag_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform tag-based search."""
        try:
            results = []
            query_lower = query_text.lower()

            # Find matching tags
            matching_tags = []
            for tag, content_ids in self.tag_index.items():
                if query_lower in tag or tag in query_lower:
                    matching_tags.extend(content_ids)

            # Remove duplicates
            unique_content_ids = list(set(matching_tags))

            for content_id in unique_content_ids[:max_results]:
                content = self.help_content.get(content_id)
                if content:
                    snippet = self._create_content_snippet(content.content, query_lower)

                    result = SearchResult(
                        result_id=str(uuid.uuid4()),
                        content_id=content_id,
                        title=content.title,
                        snippet=snippet,
                        relevance_score=0.9,  # High score for tag match
                        category=content.category,
                        content_type=content.content_type,
                        tags=content.tags,
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in tag search: {e}")
            return []

    async def _context_search(
        self, query_text: str, context: Dict[str, Any], max_results: int
    ) -> List[SearchResult]:
        """Perform context-aware search."""
        try:
            # Combine multiple search strategies based on context
            results = []

            # Get user's current context
            user_context = context.get("user_context", {})
            current_page = user_context.get("current_page", "")
            user_role = user_context.get("user_role", "")
            recent_actions = user_context.get("recent_actions", [])

            # Perform base search
            base_results = await self._keyword_search(query_text, context, max_results)

            # Boost relevance based on context
            for result in base_results:
                context_boost = 0.0

                # Boost if content matches current page
                if current_page and current_page.lower() in result.title.lower():
                    context_boost += 0.2

                # Boost if content matches user role
                if user_role and user_role.lower() in result.content.lower():
                    context_boost += 0.1

                # Boost if content matches recent actions
                for action in recent_actions:
                    if action.lower() in result.content.lower():
                        context_boost += 0.05

                # Apply context boost
                result.relevance_score = min(
                    1.0, result.relevance_score + context_boost
                )
                results.append(result)

            # Sort by updated relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results[:max_results]

        except Exception as e:
            self.logger.error(f"Error in context search: {e}")
            return []

    async def get_interactive_guide(self, guide_id: str) -> Optional[InteractiveGuide]:
        """Get an interactive guide by ID."""
        return self.interactive_guides.get(guide_id)

    async def start_interactive_guide(self, guide_id: str, user_id: str) -> bool:
        """Start an interactive guide for a user."""
        try:
            guide = self.interactive_guides.get(guide_id)
            if not guide:
                return False

            # Initialize user progress
            self.user_progress[user_id] = {
                "guide_id": guide_id,
                "current_step": 0,
                "started_at": datetime.utcnow(),
                "completed_steps": [],
                "notes": {},
            }

            self.logger.info(f"Started interactive guide {guide_id} for user {user_id}")

            return True

        except Exception as e:
            self.logger.error(f"Error starting interactive guide: {e}")
            return False

    async def _update_content_index(self):
        """Background task to update content index."""
        while True:
            try:
                # Rebuild content index
                self._rebuild_content_index()

                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Error updating content index: {e}")
                await asyncio.sleep(3600)

    def _rebuild_content_index(self):
        """Rebuild the content index."""
        try:
            # Clear existing indexes
            self.content_index.clear()
            self.tag_index.clear()
            self.category_index.clear()

            # Rebuild indexes
            for content in self.help_content.values():
                self._index_content(content)

            self.logger.info("Content index rebuilt successfully")

        except Exception as e:
            self.logger.error(f"Error rebuilding content index: {e}")

    async def _analyze_user_feedback(self):
        """Background task to analyze user feedback."""
        while True:
            try:
                # Analyze search patterns and user satisfaction
                await self._analyze_search_patterns()
                await self._analyze_user_satisfaction()

                await asyncio.sleep(7200)  # Analyze every 2 hours

            except Exception as e:
                self.logger.error(f"Error analyzing user feedback: {e}")
                await asyncio.sleep(7200)

    async def _analyze_search_patterns(self):
        """Analyze search patterns for improvement."""
        try:
            # Analyze popular search terms
            search_terms = defaultdict(int)
            for query in self.user_queries.values():
                search_terms[query.query_text.lower()] += 1

            # Find most common searches
            popular_searches = sorted(
                search_terms.items(), key=lambda x: x[1], reverse=True
            )[:10]

            self.logger.info(f"Top search terms: {popular_searches}")

        except Exception as e:
            self.logger.error(f"Error analyzing search patterns: {e}")

    async def _analyze_user_satisfaction(self):
        """Analyze user satisfaction metrics."""
        try:
            # Calculate average response time
            if self.total_queries > 0:
                avg_response_time = self.total_response_time / self.total_queries
                self.logger.info(f"Average response time: {avg_response_time:.2f}s")

            # Calculate success rate
            if self.total_queries > 0:
                success_rate = self.successful_searches / self.total_queries
                self.logger.info(f"Search success rate: {success_rate:.2%}")

        except Exception as e:
            self.logger.error(f"Error analyzing user satisfaction: {e}")

    def get_help_metrics(self) -> HelpMetrics:
        """Get help system performance metrics."""
        try:
            avg_response_time = 0.0
            if self.total_queries > 0:
                avg_response_time = self.total_response_time / self.total_queries

            user_satisfaction = 0.0
            if self.total_queries > 0:
                user_satisfaction = self.successful_searches / self.total_queries

            return HelpMetrics(
                total_content_items=self.total_content_items,
                total_queries=self.total_queries,
                successful_searches=self.successful_searches,
                average_response_time=avg_response_time,
                user_satisfaction=user_satisfaction,
                metadata={
                    "enable_semantic_search": self.enable_semantic_search,
                    "enable_fuzzy_search": self.enable_fuzzy_search,
                    "max_search_results": self.max_search_results,
                    "supported_languages": self.supported_languages,
                    "help_categories_supported": [hc.value for hc in HelpCategory],
                    "content_types_supported": [ct.value for ct in ContentType],
                    "search_types_supported": [st.value for st in SearchType],
                    "interactive_guides_count": len(self.interactive_guides),
                },
            )

        except Exception as e:
            self.logger.error(f"Error getting help metrics: {e}")
            return HelpMetrics(
                total_content_items=0,
                total_queries=0,
                successful_searches=0,
                average_response_time=0.0,
                user_satisfaction=0.0,
            )


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "enable_semantic_search": True,
        "enable_fuzzy_search": True,
        "max_search_results": 20,
        "supported_languages": ["en", "es", "fr", "de"],
    }

    # Initialize help agent
    help_agent = HelpAgent(config)

    print("HelpAgent system initialized successfully!")
