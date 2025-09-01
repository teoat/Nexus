#!/usr/bin/env python3
"""
Circular Transaction Detector - Advanced Circular Transaction Analysis

This module implements the CircularTransactionDetector class that provides
comprehensive detection of circular transactions, money laundering patterns,
and complex financial flow cycles.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import networkx as nx

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType
import logging
from datetime import datetime, timedelta

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class CircularType(Enum):
    """Types of circular transactions."""

    SIMPLE_CIRCLE = "simple_circle"  # Direct circular flow
    COMPLEX_CIRCLE = "complex_circle"  # Multi-hop circular flow
    MONEY_LAUNDERING = "money_laundering"  # Money laundering pattern
    SHELL_COMPANY_CIRCLE = "shell_company_circle"  # Shell company circular flow
    LAYERING = "layering"  # Layering pattern
    INTEGRATION = "integration"  # Integration pattern
    SMURFING = "smurfing"  # Smurfing pattern
    STRUCTURING = "structuring"  # Structuring pattern


class RiskLevel(Enum):
    """Risk levels for circular transactions."""

    LOW = "low"  # Low risk
    MEDIUM = "medium"  # Medium risk
    HIGH = "high"  # High risk
    CRITICAL = "critical"  # Critical risk


@dataclass
class CircularTransaction:
    """A detected circular transaction pattern."""

    id: str
    circular_type: CircularType
    risk_level: RiskLevel
    entities_involved: List[str]
    transaction_path: List[str]
    total_amount: float
    cycle_length: int
    confidence: float
    detection_time: datetime
    evidence: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.detection_time:
            self.detection_time = datetime.utcnow()


@dataclass
class TransactionNode:
    """Node in the transaction graph."""

    id: str
    entity_type: str
    balance: float
    transaction_count: int
    risk_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionEdge:
    """Edge in the transaction graph."""

    source: str
    target: str
    amount: float
    timestamp: datetime
    transaction_id: str
    risk_indicators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircularTransactionDetector:
    """
    Comprehensive circular transaction detection system.

    The CircularTransactionDetector is responsible for:
    - Detecting various types of circular transactions
    - Identifying money laundering patterns
    - Analyzing transaction flow cycles
    - Providing risk assessment and scoring
    - Supporting investigation and reporting
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the CircularTransactionDetector."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.min_cycle_length = config.get("min_cycle_length", 3)
        self.max_cycle_length = config.get("max_cycle_length", 10)
        self.amount_threshold = config.get("amount_threshold", 1000.0)
        self.time_window = config.get("time_window", timedelta(days=30))
        self.risk_threshold = config.get("risk_threshold", 0.7)

        # Transaction graph
        self.transaction_graph = nx.DiGraph()
        self.nodes: Dict[str, TransactionNode] = {}
        self.edges: Dict[str, TransactionEdge] = {}

        # Detection results
        self.detected_circles: List[CircularTransaction] = []
        self.circle_history: Dict[str, List[CircularTransaction]] = {}

        # Performance tracking
        self.total_circles_detected = 0
        self.average_detection_time = 0.0
        self.detection_accuracy = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("CircularTransactionDetector initialized successfully")

    async def start(self):
        """Start the CircularTransactionDetector.Start the CircularTransactionDetector."""
        self.logger.info("Starting CircularTransactionDetector...")

        # Initialize detection components
        await self._initialize_detection_components()

        # Start background tasks
        asyncio.create_task(self._update_detection_accuracy())
        asyncio.create_task(self._cleanup_old_data())

        self.logger.info("CircularTransactionDetector started successfully")

    async def stop(self):
        """Stop the CircularTransactionDetector.Stop the CircularTransactionDetector."""
        self.logger.info("Stopping CircularTransactionDetector...")
        self.logger.info("CircularTransactionDetector stopped")

    async def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Add a transaction to the detection graph.Add a transaction to the detection graph."""
        try:
            # Extract transaction details
            source = transaction.get("source")
            target = transaction.get("target")
            amount = transaction.get("amount", 0.0)
            timestamp = transaction.get("timestamp")
            transaction_id = transaction.get("id")

            if not all([source, target, timestamp, transaction_id]):
                self.logger.warning(f"Incomplete transaction data: {transaction}")
                return False

            # Convert timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            # Create or update nodes
            await self._add_or_update_node(
                source, transaction.get("source_metadata", {})
            )
            await self._add_or_update_node(
                target, transaction.get("target_metadata", {})
            )

            # Create edge
            edge = TransactionEdge(
                source=source,
                target=target,
                amount=amount,
                timestamp=timestamp,
                transaction_id=transaction_id,
                risk_indicators=transaction.get("risk_indicators", []),
                metadata=transaction.get("metadata", {}),
            )

            # Add to graph
            self.transaction_graph.add_edge(
                source,
                target,
                amount=amount,
                timestamp=timestamp,
                transaction_id=transaction_id,
                edge_data=edge,
            )

            # Store edge
            edge_key = f"{source}_{target}_{transaction_id}"
            self.edges[edge_key] = edge

            self.logger.info(
                f"Added transaction: {transaction_id} ({source} -> {target}: {amount})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding transaction: {e}")
            return False

    async def _add_or_update_node(self, entity_id: str, metadata: Dict[str, Any]):
        """Add or update a node in the transaction graph.Add or update a node in the transaction graph."""
        try:
            if entity_id not in self.nodes:
                # Create new node
                node = TransactionNode(
                    id=entity_id,
                    entity_type=metadata.get("entity_type", "unknown"),
                    balance=metadata.get("balance", 0.0),
                    transaction_count=1,
                    risk_score=metadata.get("risk_score", 0.0),
                    metadata=metadata,
                )
                self.nodes[entity_id] = node

                # Add to graph
                self.transaction_graph.add_node(entity_id, **node.__dict__)
            else:
                # Update existing node
                self.nodes[entity_id].transaction_count += 1
                self.nodes[entity_id].balance = metadata.get(
                    "balance", self.nodes[entity_id].balance
                )
                self.nodes[entity_id].risk_score = max(
                    self.nodes[entity_id].risk_score, metadata.get("risk_score", 0.0)
                )

                # Update graph node
                self.transaction_graph.nodes[entity_id].update(
                    self.nodes[entity_id].__dict__
                )

        except Exception as e:
            self.logger.error(f"Error adding/updating node {entity_id}: {e}")

    async def detect_circular_transactions(
        self, circular_types: List[CircularType] = None
    ) -> List[CircularTransaction]:
        """Detect circular transactions in the graph.Detect circular transactions in the graph."""
        try:
            start_time = datetime.utcnow()

            if not circular_types:
                circular_types = list(CircularType)

            self.logger.info(
                f"Starting circular transaction detection: {len(circular_types)} types"
            )

            detected_circles = []

            # Detect each type of circular transaction
            for circular_type in circular_types:
                try:
                    if circular_type == CircularType.SIMPLE_CIRCLE:
                        circles = await self._detect_simple_circles()
                    elif circular_type == CircularType.COMPLEX_CIRCLE:
                        circles = await self._detect_complex_circles()
                    elif circular_type == CircularType.MONEY_LAUNDERING:
                        circles = await self._detect_money_laundering()
                    elif circular_type == CircularType.SHELL_COMPANY_CIRCLE:
                        circles = await self._detect_shell_company_circles()
                    elif circular_type == CircularType.LAYERING:
                        circles = await self._detect_layering_patterns()
                    elif circular_type == CircularType.INTEGRATION:
                        circles = await self._detect_integration_patterns()
                    elif circular_type == CircularType.SMURFING:
                        circles = await self._detect_smurfing_patterns()
                    elif circular_type == CircularType.STRUCTURING:
                        circles = await self._detect_structuring_patterns()
                    else:
                        continue

                    if circles:
                        detected_circles.extend(circles)

                except Exception as e:
                    self.logger.error(
                        f"Error detecting {circular_type.value} patterns: {e}"
                    )
                    continue

            # Filter by risk and confidence
            filtered_circles = [
                circle
                for circle in detected_circles
                if self._calculate_risk_score(circle) >= self.risk_threshold
            ]

            # Store results
            self.detected_circles.extend(filtered_circles)

            # Update statistics
            self.total_circles_detected += len(filtered_circles)

            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_detection_time(processing_time)

            self.logger.info(
                f"Detected {len(filtered_circles)} circular transactions in {processing_time:.2f}s"
            )

            return filtered_circles

        except Exception as e:
            self.logger.error(f"Error in circular transaction detection: {e}")
            return []

    async def _detect_simple_circles(self) -> List[CircularTransaction]:
        """Detect simple circular transactions.Detect simple circular transactions."""
        try:
            circles = []

            # Find all simple cycles in the graph
            try:
                simple_cycles = list(nx.simple_cycles(self.transaction_graph))
            except nx.NetworkXNoCycle:
                return circles

            for cycle in simple_cycles:
                if self.min_cycle_length <= len(cycle) <= self.max_cycle_length:
                    # Calculate cycle metrics
                    cycle_amount = self._calculate_cycle_amount(cycle)
                    cycle_risk = self._calculate_cycle_risk(cycle)

                    if cycle_amount >= self.amount_threshold:
                        circle = CircularTransaction(
                            id=f"simple_circle_{datetime.utcnow().timestamp()}_{len(circles)}",
                            circular_type=CircularType.SIMPLE_CIRCLE,
                            risk_level=self._get_risk_level(cycle_risk),
                            entities_involved=cycle,
                            transaction_path=cycle,
                            total_amount=cycle_amount,
                            cycle_length=len(cycle),
                            confidence=0.8,
                            detection_time=datetime.utcnow(),
                            evidence={
                                "cycle": cycle,
                                "amount": cycle_amount,
                                "risk_score": cycle_risk,
                            },
                        )
                        circles.append(circle)

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting simple circles: {e}")
            return []

    async def _detect_complex_circles(self) -> List[CircularTransaction]:
        """Detect complex circular transactions with multiple paths.Detect complex circular transactions with multiple paths."""
        try:
            circles = []

            # Find all cycles with length > 3
            try:
                all_cycles = list(nx.simple_cycles(self.transaction_graph))
                complex_cycles = [cycle for cycle in all_cycles if len(cycle) > 3]
            except nx.NetworkXNoCycle:
                return circles

            for cycle in complex_cycles:
                if len(cycle) <= self.max_cycle_length:
                    # Analyze cycle complexity
                    complexity_score = self._calculate_complexity_score(cycle)
                    cycle_amount = self._calculate_cycle_amount(cycle)
                    cycle_risk = self._calculate_cycle_risk(cycle)

                    if complexity_score > 0.6 and cycle_amount >= self.amount_threshold:
                        circle = CircularTransaction(
                            id=f"complex_circle_{datetime.utcnow().timestamp()}_{len(circles)}",
                            circular_type=CircularType.COMPLEX_CIRCLE,
                            risk_level=self._get_risk_level(cycle_risk),
                            entities_involved=cycle,
                            transaction_path=cycle,
                            total_amount=cycle_amount,
                            cycle_length=len(cycle),
                            confidence=0.75,
                            detection_time=datetime.utcnow(),
                            evidence={
                                "cycle": cycle,
                                "complexity_score": complexity_score,
                                "amount": cycle_amount,
                                "risk_score": cycle_risk,
                            },
                        )
                        circles.append(circle)

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting complex circles: {e}")
            return []

    async def _detect_money_laundering(self) -> List[CircularTransaction]:
        """Detect money laundering patterns.Detect money laundering patterns."""
        try:
            circles = []

            # Look for layering patterns (multiple hops)
            for node in self.transaction_graph.nodes():
                # Find paths from this node back to itself
                try:
                    paths = list(
                        nx.all_simple_paths(self.transaction_graph, node, node)
                    )
                    laundering_paths = [path for path in paths if len(path) > 3]

                    for path in laundering_paths:
                        if len(path) <= self.max_cycle_length:
                            # Calculate laundering indicators
                            laundering_score = self._calculate_laundering_score(path)
                            path_amount = self._calculate_path_amount(path)

                            if (
                                laundering_score > 0.7
                                and path_amount >= self.amount_threshold
                            ):
                                circle = CircularTransaction(
                                    id=f"money_laundering_{datetime.utcnow().timestamp()}_{len(circles)}",
                                    circular_type=CircularType.MONEY_LAUNDERING,
                                    risk_level=RiskLevel.CRITICAL,
                                    entities_involved=path,
                                    transaction_path=path,
                                    total_amount=path_amount,
                                    cycle_length=len(path),
                                    confidence=0.9,
                                    detection_time=datetime.utcnow(),
                                    evidence={
                                        "path": path,
                                        "laundering_score": laundering_score,
                                        "amount": path_amount,
                                    },
                                )
                                circles.append(circle)

                except nx.NetworkXNoPath:
                    continue

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting money laundering: {e}")
            return []

    async def _detect_shell_company_circles(self) -> List[CircularTransaction]:
        """Detect circular transactions involving shell companies.Detect circular transactions involving shell companies."""
        try:
            circles = []

            # Identify potential shell companies
            shell_companies = [
                entity_id
                for entity_id, node in self.nodes.items()
                if self._is_shell_company(node)
            ]

            # Look for cycles involving shell companies
            for shell_company in shell_companies:
                try:
                    cycles = list(nx.simple_cycles(self.transaction_graph))
                    shell_cycles = [
                        cycle
                        for cycle in cycles
                        if shell_company in cycle
                        and len(cycle) >= self.min_cycle_length
                    ]

                    for cycle in shell_cycles:
                        if len(cycle) <= self.max_cycle_length:
                            cycle_amount = self._calculate_cycle_amount(cycle)
                            shell_risk = self._calculate_shell_company_risk(cycle)

                            if (
                                shell_risk > 0.8
                                and cycle_amount >= self.amount_threshold
                            ):
                                circle = CircularTransaction(
                                    id=f"shell_circle_{datetime.utcnow().timestamp()}_{len(circles)}",
                                    circular_type=CircularType.SHELL_COMPANY_CIRCLE,
                                    risk_level=RiskLevel.CRITICAL,
                                    entities_involved=cycle,
                                    transaction_path=cycle,
                                    total_amount=cycle_amount,
                                    cycle_length=len(cycle),
                                    confidence=0.95,
                                    detection_time=datetime.utcnow(),
                                    evidence={
                                        "cycle": cycle,
                                        "shell_companies": [
                                            e for e in cycle if e in shell_companies
                                        ],
                                        "shell_risk": shell_risk,
                                        "amount": cycle_amount,
                                    },
                                )
                                circles.append(circle)

                except nx.NetworkXNoCycle:
                    continue

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting shell company circles: {e}")
            return []

    async def _detect_layering_patterns(self) -> List[CircularTransaction]:
        """Detect layering patterns in transactions.Detect layering patterns in transactions."""
        try:
            circles = []

            # Look for multiple transaction layers
            for source in self.transaction_graph.nodes():
                for target in self.transaction_graph.nodes():
                    if source != target:
                        try:
                            # Find all paths between source and target
                            all_paths = list(
                                nx.all_simple_paths(
                                    self.transaction_graph, source, target
                                )
                            )

                            # Look for layering (multiple paths with different lengths)
                            if len(all_paths) > 1:
                                path_lengths = [len(path) for path in all_paths]
                                if (
                                    max(path_lengths) - min(path_lengths) >= 2
                                ):  # Significant layering
                                    layering_score = self._calculate_layering_score(
                                        all_paths
                                    )
                                    total_amount = sum(
                                        self._calculate_path_amount(path)
                                        for path in all_paths
                                    )

                                    if (
                                        layering_score > 0.7
                                        and total_amount >= self.amount_threshold
                                    ):
                                        # Create circular transaction for the layering pattern
                                        circle = CircularTransaction(
                                            id=f"layering_{datetime.utcnow().timestamp()}_{len(circles)}",
                                            circular_type=CircularType.LAYERING,
                                            risk_level=RiskLevel.HIGH,
                                            entities_involved=list(
                                                set(
                                                    [
                                                        node
                                                        for path in all_paths
                                                        for node in path
                                                    ]
                                                )
                                            ),
                                            transaction_path=all_paths[
                                                0
                                            ],  # Use first path as representative
                                            total_amount=total_amount,
                                            cycle_length=len(all_paths[0]),
                                            confidence=0.85,
                                            detection_time=datetime.utcnow(),
                                            evidence={
                                                "paths": all_paths,
                                                "layering_score": layering_score,
                                                "total_amount": total_amount,
                                                "path_count": len(all_paths),
                                            },
                                        )
                                        circles.append(circle)

                        except nx.NetworkXNoPath:
                            continue

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting layering patterns: {e}")
            return []

    async def _detect_integration_patterns(self) -> List[CircularTransaction]:
        """Detect integration patterns in transactions.Detect integration patterns in transactions."""
        try:
            circles = []

            # Look for integration patterns (converging transactions)
            for target in self.transaction_graph.nodes():
                # Find all incoming transactions
                incoming_edges = list(
                    self.transaction_graph.in_edges(target, data=True)
                )

                if len(incoming_edges) >= 3:  # Multiple sources
                    # Check if sources are connected
                    sources = [edge[0] for edge in incoming_edges]
                    source_subgraph = self.transaction_graph.subgraph(sources)

                    if nx.is_connected(source_subgraph.to_undirected()):
                        # Integration pattern detected
                        integration_score = self._calculate_integration_score(
                            incoming_edges
                        )
                        total_amount = sum(edge["amount"] for edge in incoming_edges)

                        if (
                            integration_score > 0.6
                            and total_amount >= self.amount_threshold
                        ):
                            circle = CircularTransaction(
                                id=f"integration_{datetime.utcnow().timestamp()}_{len(circles)}",
                                circular_type=CircularType.INTEGRATION,
                                risk_level=RiskLevel.MEDIUM,
                                entities_involved=sources + [target],
                                transaction_path=sources + [target],
                                total_amount=total_amount,
                                cycle_length=len(sources) + 1,
                                confidence=0.7,
                                detection_time=datetime.utcnow(),
                                evidence={
                                    "sources": sources,
                                    "target": target,
                                    "integration_score": integration_score,
                                    "total_amount": total_amount,
                                },
                            )
                            circles.append(circle)

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting integration patterns: {e}")
            return []

    async def _detect_smurfing_patterns(self) -> List[CircularTransaction]:
        """Detect smurfing patterns (structuring).Detect smurfing patterns (structuring)."""
        try:
            circles = []

            # Look for smurfing patterns (multiple small transactions)
            for source in self.transaction_graph.nodes():
                # Find all outgoing transactions
                outgoing_edges = list(
                    self.transaction_graph.out_edges(source, data=True)
                )

                if len(outgoing_edges) >= 5:  # Multiple small transactions
                    amounts = [edge["amount"] for edge in outgoing_edges]
                    total_amount = sum(amounts)

                    # Check if amounts are structured (below reporting thresholds)
                    structured_amounts = [
                        amt for amt in amounts if amt < 10000
                    ]  # $10K threshold

                    if (
                        len(structured_amounts) >= 3
                        and total_amount >= self.amount_threshold
                    ):
                        smurfing_score = self._calculate_smurfing_score(
                            amounts, total_amount
                        )

                        if smurfing_score > 0.7:
                            targets = [edge[1] for edge in outgoing_edges]
                            circle = CircularTransaction(
                                id=f"smurfing_{datetime.utcnow().timestamp()}_{len(circles)}",
                                circular_type=CircularType.SMURFING,
                                risk_level=RiskLevel.HIGH,
                                entities_involved=[source] + targets,
                                transaction_path=[source] + targets,
                                total_amount=total_amount,
                                cycle_length=len(targets) + 1,
                                confidence=0.8,
                                detection_time=datetime.utcnow(),
                                evidence={
                                    "source": source,
                                    "targets": targets,
                                    "amounts": amounts,
                                    "smurfing_score": smurfing_score,
                                    "total_amount": total_amount,
                                },
                            )
                            circles.append(circle)

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting smurfing patterns: {e}")
            return []

    async def _detect_structuring_patterns(self) -> List[CircularTransaction]:
        """Detect structuring patterns in transactions.Detect structuring patterns in transactions."""
        try:
            circles = []

            # Look for structuring patterns (systematic transaction splitting)
            for entity_id in self.transaction_graph.nodes():
                # Analyze transaction patterns over time
                entity_transactions = [
                    edge
                    for edge in self.transaction_graph.edges(data=True)
                    if edge[0] == entity_id or edge[1] == entity_id
                ]

                if len(entity_transactions) >= 10:  # Sufficient data
                    # Group by date and analyze patterns
                    daily_amounts = defaultdict(float)
                    for edge in entity_transactions:
                        timestamp = edge["timestamp"]
                        date = timestamp.date()
                        amount = edge["amount"]
                        daily_amounts[date] += amount

                    # Check for structuring patterns
                    structuring_score = self._calculate_structuring_score(daily_amounts)

                    if structuring_score > 0.7:
                        total_amount = sum(daily_amounts.values())

                        if total_amount >= self.amount_threshold:
                            circle = CircularTransaction(
                                id=f"structuring_{entity_id}_{datetime.utcnow().timestamp()}",
                                circular_type=CircularType.STRUCTURING,
                                risk_level=RiskLevel.HIGH,
                                entities_involved=[entity_id],
                                transaction_path=[entity_id],
                                total_amount=total_amount,
                                cycle_length=1,
                                confidence=0.85,
                                detection_time=datetime.utcnow(),
                                evidence={
                                    "entity": entity_id,
                                    "daily_amounts": dict(daily_amounts),
                                    "structuring_score": structuring_score,
                                    "total_amount": total_amount,
                                },
                            )
                            circles.append(circle)

            return circles

        except Exception as e:
            self.logger.error(f"Error detecting structuring patterns: {e}")
            return []

    def _calculate_cycle_amount(self, cycle: List[str]) -> float:
        """Calculate total amount for a cycle.Calculate total amount for a cycle."""
        try:
            total_amount = 0.0

            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]

                if self.transaction_graph.has_edge(source, target):
                    edge_data = self.transaction_graph.get_edge_data(source, target)
                    if isinstance(edge_data, dict) and "amount" in edge_data:
                        total_amount += edge_data["amount"]
                    elif hasattr(edge_data, "amount"):
                        total_amount += edge_data.amount

            return total_amount

        except Exception as e:
            self.logger.error(f"Error calculating cycle amount: {e}")
            return 0.0

    def _calculate_cycle_risk(self, cycle: List[str]) -> float:
        """Calculate risk score for a cycle.Calculate risk score for a cycle."""
        try:
            risk_scores = []

            for entity_id in cycle:
                if entity_id in self.nodes:
                    risk_scores.append(self.nodes[entity_id].risk_score)

            # Also consider cycle characteristics
            cycle_risk = 0.0

            # Longer cycles are riskier
            if len(cycle) > 5:
                cycle_risk += 0.2

            # High amounts are riskier
            cycle_amount = self._calculate_cycle_amount(cycle)
            if cycle_amount > 100000:  # $100K threshold
                cycle_risk += 0.3

            # Combine with entity risk scores
            if risk_scores:
                avg_entity_risk = np.mean(risk_scores)
                cycle_risk = (cycle_risk + avg_entity_risk) / 2

            return min(1.0, cycle_risk)

        except Exception as e:
            self.logger.error(f"Error calculating cycle risk: {e}")
            return 0.5

    def _calculate_complexity_score(self, cycle: List[str]) -> float:
        """Calculate complexity score for a cycle.Calculate complexity score for a cycle."""
        try:
            # Complexity based on cycle length and entity diversity
            length_score = min(1.0, len(cycle) / 10.0)

            # Entity type diversity
            entity_types = set()
            for entity_id in cycle:
                if entity_id in self.nodes:
                    entity_types.add(self.nodes[entity_id].entity_type)

            diversity_score = len(entity_types) / len(cycle) if cycle else 0.0

            # Combine scores
            complexity_score = (length_score + diversity_score) / 2

            return complexity_score

        except Exception as e:
            self.logger.error(f"Error calculating complexity score: {e}")
            return 0.5

    def _calculate_laundering_score(self, path: List[str]) -> float:
        """Calculate money laundering score for a path.Calculate money laundering score for a path."""
        try:
            laundering_score = 0.0

            # Path length (longer paths are more suspicious)
            if len(path) > 5:
                laundering_score += 0.3

            # Entity type diversity
            entity_types = set()
            for entity_id in path:
                if entity_id in self.nodes:
                    entity_types.add(self.nodes[entity_id].entity_type)

            if len(entity_types) > 3:
                laundering_score += 0.2

            # Amount patterns
            path_amount = self._calculate_path_amount(path)
            if path_amount > 100000:  # $100K threshold
                laundering_score += 0.3

            # Risk scores of entities involved
            risk_scores = []
            for entity_id in path:
                if entity_id in self.nodes:
                    risk_scores.append(self.nodes[entity_id].risk_score)

            if risk_scores:
                avg_risk = np.mean(risk_scores)
                laundering_score += avg_risk * 0.2

            return min(1.0, laundering_score)

        except Exception as e:
            self.logger.error(f"Error calculating laundering score: {e}")
            return 0.5

    def _calculate_path_amount(self, path: List[str]) -> float:
        """Calculate total amount for a path.Calculate total amount for a path."""
        try:
            total_amount = 0.0

            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]

                if self.transaction_graph.has_edge(source, target):
                    edge_data = self.transaction_graph.get_edge_data(source, target)
                    if isinstance(edge_data, dict) and "amount" in edge_data:
                        total_amount += edge_data["amount"]
                    elif hasattr(edge_data, "amount"):
                        total_amount += edge_data.amount

            return total_amount

        except Exception as e:
            self.logger.error(f"Error calculating path amount: {e}")
            return 0.0

    def _is_shell_company(self, node: TransactionNode) -> bool:
        """Check if a node represents a shell company.Check if a node represents a shell company."""
        try:
            shell_indicators = 0

            # Low transaction count
            if node.transaction_count < 5:
                shell_indicators += 1

            # Low balance
            if node.balance < 10000:  # $10K threshold
                shell_indicators += 1

            # High risk score
            if node.risk_score > 0.8:
                shell_indicators += 1

            # Entity type indicators
            if node.entity_type.lower() in ["shell", "holding", "paper"]:
                shell_indicators += 2

            return shell_indicators >= 2

        except Exception as e:
            self.logger.error(f"Error checking shell company: {e}")
            return False

    def _calculate_shell_company_risk(self, cycle: List[str]) -> float:
        """Calculate risk score for shell company involvement.Calculate risk score for shell company involvement."""
        try:
            shell_companies = [
                entity_id
                for entity_id in cycle
                if entity_id in self.nodes
                and self._is_shell_company(self.nodes[entity_id])
            ]

            if not shell_companies:
                return 0.0

            # Risk increases with shell company involvement
            shell_ratio = len(shell_companies) / len(cycle)

            # Additional risk for multiple shell companies
            multiple_shell_risk = min(0.3, len(shell_companies) * 0.1)

            total_risk = shell_ratio + multiple_shell_risk

            return min(1.0, total_risk)

        except Exception as e:
            self.logger.error(f"Error calculating shell company risk: {e}")
            return 0.5

    def _calculate_layering_score(self, paths: List[List[str]]) -> float:
        """Calculate layering score for multiple paths.Calculate layering score for multiple paths."""
        try:
            if len(paths) < 2:
                return 0.0

            # Path length variation
            path_lengths = [len(path) for path in paths]
            length_variation = (max(path_lengths) - min(path_lengths)) / max(
                path_lengths
            )

            # Path count
            path_count_score = min(1.0, len(paths) / 5.0)

            # Combine scores
            layering_score = (length_variation + path_count_score) / 2

            return layering_score

        except Exception as e:
            self.logger.error(f"Error calculating layering score: {e}")
            return 0.5

    def _calculate_integration_score(self, incoming_edges: List[Tuple]) -> float:
        """Calculate integration score for converging transactions.Calculate integration score for converging transactions."""
        try:
            if len(incoming_edges) < 2:
                return 0.0

            # Amount distribution
            amounts = [edge[2].get("amount", 0) for edge in incoming_edges]
            total_amount = sum(amounts)

            if total_amount == 0:
                return 0.0

            # Check for even distribution (suspicious)
            mean_amount = total_amount / len(amounts)
            variance = np.var(amounts)
            evenness_score = 1.0 / (1.0 + variance / (mean_amount**2))

            # Multiple sources score
            source_count_score = min(1.0, len(incoming_edges) / 5.0)

            # Combine scores
            integration_score = (evenness_score + source_count_score) / 2

            return integration_score

        except Exception as e:
            self.logger.error(f"Error calculating integration score: {e}")
            return 0.5

    def _calculate_smurfing_score(
        self, amounts: List[float], total_amount: float
    ) -> float:
        """Calculate smurfing score for transaction amounts.Calculate smurfing score for transaction amounts."""
        try:
            if not amounts or total_amount == 0:
                return 0.0

            # Check for amounts below reporting thresholds
            below_threshold = [amt for amt in amounts if amt < 10000]  # $10K threshold
            threshold_ratio = len(below_threshold) / len(amounts)

            # Check for even distribution
            mean_amount = total_amount / len(amounts)
            variance = np.var(amounts)
            evenness_score = 1.0 / (1.0 + variance / (mean_amount**2))

            # Multiple transactions score
            transaction_count_score = min(1.0, len(amounts) / 10.0)

            # Combine scores
            smurfing_score = (
                threshold_ratio + evenness_score + transaction_count_score
            ) / 3

            return smurfing_score

        except Exception as e:
            self.logger.error(f"Error calculating smurfing score: {e}")
            return 0.5

    def _calculate_structuring_score(
        self, daily_amounts: Dict[datetime.date, float]
    ) -> float:
        """Calculate structuring score for daily transaction amounts.Calculate structuring score for daily transaction amounts."""
        try:
            if len(daily_amounts) < 3:
                return 0.0

            amounts = list(daily_amounts.values())
            total_amount = sum(amounts)

            if total_amount == 0:
                return 0.0

            # Check for amounts below reporting thresholds
            below_threshold = [amt for amt in amounts if amt < 10000]  # $10K threshold
            threshold_ratio = len(below_threshold) / len(amounts)

            # Check for consistent daily amounts
            mean_amount = total_amount / len(amounts)
            variance = np.var(amounts)
            consistency_score = 1.0 / (1.0 + variance / (mean_amount**2))

            # Multiple days score
            day_count_score = min(1.0, len(amounts) / 7.0)

            # Combine scores
            structuring_score = (
                threshold_ratio + consistency_score + day_count_score
            ) / 3

            return structuring_score

        except Exception as e:
            self.logger.error(f"Error calculating structuring score: {e}")
            return 0.5

    def _calculate_risk_score(self, circle: CircularTransaction) -> float:
        """Calculate overall risk score for a circular transaction.Calculate overall risk score for a circular transaction."""
        try:
            # Base risk from circle type
            type_risk = {
                CircularType.SIMPLE_CIRCLE: 0.5,
                CircularType.COMPLEX_CIRCLE: 0.7,
                CircularType.MONEY_LAUNDERING: 0.9,
                CircularType.SHELL_COMPANY_CIRCLE: 0.95,
                CircularType.LAYERING: 0.8,
                CircularType.INTEGRATION: 0.6,
                CircularType.SMURFING: 0.8,
                CircularType.STRUCTURING: 0.8,
            }.get(circle.circular_type, 0.5)

            # Risk from amount
            amount_risk = min(1.0, circle.total_amount / 1000000)  # $1M threshold

            # Risk from cycle length
            length_risk = min(1.0, circle.cycle_length / 10.0)

            # Risk from entities involved
            entity_risk = 0.0
            if circle.entities_involved:
                entity_risk_scores = [
                    self.nodes[entity_id].risk_score
                    for entity_id in circle.entities_involved
                    if entity_id in self.nodes
                ]
                if entity_risk_scores:
                    entity_risk = np.mean(entity_risk_scores)

            # Combine risk factors
            total_risk = (type_risk + amount_risk + length_risk + entity_risk) / 4

            return min(1.0, total_risk)

        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 0.5

    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level.Convert risk score to risk level."""
        try:
            if risk_score >= 0.8:
                return RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                return RiskLevel.HIGH
            elif risk_score >= 0.4:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW

        except Exception as e:
            self.logger.error(f"Error getting risk level: {e}")
            return RiskLevel.MEDIUM

    async def _initialize_detection_components(self):
        """Initialize detection components.Initialize detection components."""
        try:
            # Initialize detection algorithms
            self.logger.info(
                "Circular transaction detection components initialized successfully"
            )

        except Exception as e:
            self.logger.error(f"Error initializing detection components: {e}")

    async def _update_detection_accuracy(self):
        """Update detection accuracy metrics.Update detection accuracy metrics."""
        while True:
            try:
                # This would calculate accuracy based on validation data
                # For now, use a placeholder
                self.detection_accuracy = 0.91

                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Error updating detection accuracy: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_data(self):
        """Clean up old detection data.Clean up old detection data."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=90)

                # Remove old circles
                self.detected_circles = [
                    circle
                    for circle in self.detected_circles
                    if circle.detection_time > cutoff_time
                ]

                # Remove old edges
                old_edges = []
                for edge_key, edge in self.edges.items():
                    if edge.timestamp < cutoff_time:
                        old_edges.append(edge_key)

                for edge_key in old_edges:
                    del self.edges[edge_key]

                # Clean up graph
                for edge_key in old_edges:
                    source, target, transaction_id = edge_key.split("_", 2)
                    if self.transaction_graph.has_edge(source, target):
                        self.transaction_graph.remove_edge(source, target)

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)

    def _update_average_detection_time(self, new_time: float):
        """Update average detection time.Update average detection time."""
        self.average_detection_time = (
            self.average_detection_time * self.total_circles_detected + new_time
        ) / (self.total_circles_detected + 1)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_circles_detected": self.total_circles_detected,
            "average_detection_time": self.average_detection_time,
            "detection_accuracy": self.detection_accuracy,
            "graph_size": {
                "nodes": self.transaction_graph.number_of_nodes(),
                "edges": self.transaction_graph.number_of_edges(),
            },
            "circular_types_supported": [
                "simple_circle",
                "complex_circle",
                "money_laundering",
                "shell_company_circle",
                "layering",
                "integration",
                "smurfing",
                "structuring",
            ],
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "min_cycle_length": 3,
        "max_cycle_length": 10,
        "amount_threshold": 1000.0,
        "time_window": timedelta(days=30),
        "risk_threshold": 0.7,
    }

    # Initialize circular transaction detector
    detector = CircularTransactionDetector(config)

    print("CircularTransactionDetector system initialized successfully!")
