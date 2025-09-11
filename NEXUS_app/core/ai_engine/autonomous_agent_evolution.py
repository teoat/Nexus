"""
autonomous_agent_evolution Module

Autonomous Agent Evolution

This module provides functionality for autonomous agent evolution.

Classes:
    TBD: Add class descriptions

Functions:
    TBD: Add function descriptions

Example:
    TBD: Add usage example

Author: NEXUS Platform
Created: 2025-09-11
Version: 1.0.0
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import random
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EvolutionStage(Enum):
    """Stages of agent evolution."""
    INITIALIZATION = "initialization"
    LEARNING = "learning"
    ADAPTATION = "adaptation"
    OPTIMIZATION = "optimization"
    MASTERY = "mastery"

class AgentType(Enum):
    """Types of AI agents."""
    GENERALIST = "generalist"
    COORDINATOR = "coordinator"
    ANALYST = "analyst"
    CREATOR = "creator"
    OPTIMIZER = "optimizer"

@dataclass
class AgentGenome:
    """Represents the genetic code of an AI agent."""
    agent_id: str
    agent_type: AgentType
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    learning_rate: float
    adaptation_threshold: float
    collaboration_preferences: List[str]
    mutation_rate: float
    fitness_score: float
    generation: int
    parent_ids: List[str]
    created_at: datetime

class AutonomousAgentEvolution:
    """
    Autonomous Agent Evolution System for Frenly AI.
    Implements genetic algorithms and evolutionary strategies for AI agent improvement.
    """

    def __init__(self, config: Dict[str, Any]):
        """
          Init  
        
        
        Args:
            config: Description of config
    
        Example:
            TBD: Add usage example
        """
        self.config = config
        self.population_size = config.get("population_size", 100)
        self.mutation_rate = config.get("mutation_rate", 0.1)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.selection_pressure = config.get("selection_pressure", 0.2)
        self.elite_percentage = config.get("elite_percentage", 0.1)
        self.max_generations = config.get("max_generations", 1000)
        
        # Evolution tracking
        self.current_generation = 0
        self.agent_population: List[AgentGenome] = []
        self.evolution_history: List[Dict[str, Any]] = []
        self.performance_tracker: Dict[str, List[float]] = {}
        
        # Initialize population
        self._initialize_population()
        logger.info("✅ Autonomous Agent Evolution System initialized")

    def _initialize_population(self):
        """Initialize the initial population of AI agents."""
        try:
            for i in range(self.population_size):
                agent = self._create_random_agent(f"agent_{i}")
                self.agent_population.append(agent)
            
            logger.info(f"✅ Initialized population of {self.population_size} agents")
        except Exception as e:
            logger.error(f"Failed to initialize population: {e}")

    def _create_random_agent(self, agent_id: str) -> AgentGenome:
        """Create a random agent genome."""
        agent_type = random.choice(list(AgentType))
        capabilities = self._generate_random_capabilities()
        performance_metrics = self._generate_random_metrics()
        
        return AgentGenome(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities,
            performance_metrics=performance_metrics,
            learning_rate=random.uniform(0.001, 0.1),
            adaptation_threshold=random.uniform(0.1, 0.9),
            mutation_rate=random.uniform(0.01, 0.2),
            fitness_score=0.0,
            generation=0,
            parent_ids=[],
            created_at=datetime.now()
        )

    def _generate_random_capabilities(self) -> List[str]:
        """Generate random capabilities for an agent."""
        all_capabilities = [
            "natural_language_processing", "computer_vision", "predictive_analytics",
            "pattern_recognition", "decision_making", "problem_solving",
            "creativity", "collaboration", "learning", "adaptation",
            "optimization", "reasoning", "memory", "attention",
            "planning", "execution", "monitoring", "evaluation"
        ]

    def _generate_random_metrics(self) -> Dict[str, float]:
        """Generate random performance metrics."""
        return {
            "accuracy": random.uniform(0.5, 1.0),
            "efficiency": random.uniform(0.3, 1.0),
            "creativity": random.uniform(0.2, 1.0),
            "collaboration": random.uniform(0.4, 1.0),
            "adaptability": random.uniform(0.3, 1.0),
            "reliability": random.uniform(0.6, 1.0)
        }

    async def evaluate_fitness(self, agent: AgentGenome, task_context: Dict[str, Any]) -> float:
        """
        Evaluate the fitness of an agent based on task performance.
        """
        try:
            base_fitness = sum(agent.performance_metrics.values()) / len(agent.performance_metrics)
            
            context_bonus = 0.0
            if task_context.get("requires_creativity") and "creativity" in agent.capabilities:
                context_bonus += 0.2
            if task_context.get("requires_collaboration") and "collaboration" in agent.capabilities:
                context_bonus += 0.15
            if task_context.get("requires_adaptation") and "adaptation" in agent.capabilities:
                context_bonus += 0.1
            
            
            agent.fitness_score = fitness
            
            return fitness

        except Exception as e:
            logger.error(f"Failed to evaluate fitness for agent {agent.agent_id}: {e}")
            return 0.0

    async def evolve_generation(self, task_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evolve the current generation of agents.
        """
        try:
            # Evaluate fitness for all agents
            for agent in self.agent_population:
                for context in task_contexts:
                    await self.evaluate_fitness(agent, context)
            
            # Sort agents by fitness
            self.agent_population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            # Track generation statistics
            generation_stats = self._calculate_generation_stats()
            self.evolution_history.append(generation_stats)
            
            # Create next generation
            next_generation = await self._create_next_generation()
            
            # Replace current population
            self.agent_population = next_generation
            self.current_generation += 1
            
            logger.info(f"✅ Generation {self.current_generation} evolved. Best fitness: {generation_stats['best_fitness']:.3f}")
            return generation_stats

        except Exception as e:
            logger.error(f"Failed to evolve generation: {e}")
            raise

    def _calculate_generation_stats(self) -> Dict[str, Any]:
        """Calculate statistics for the current generation."""
        fitness_scores = [agent.fitness_score for agent in self.agent_population]
        
        return {
            "generation": self.current_generation,
            "best_fitness": max(fitness_scores),
            "average_fitness": sum(fitness_scores) / len(fitness_scores),
            "worst_fitness": min(fitness_scores),
            "fitness_std": np.std(fitness_scores) if len(fitness_scores) > 1 else 0,
            "population_size": len(self.agent_population),
            "timestamp": datetime.now().isoformat()
        }

    async def _create_next_generation(self) -> List[AgentGenome]:
        """Create the next generation of agents."""
        next_generation = []
        
        # Elitism: Keep best agents
        elite_count = int(self.population_size * self.elite_percentage)
        for i in range(elite_count):
            elite_agent = self._clone_agent(self.agent_population[i])
            elite_agent.generation = self.current_generation + 1
            next_generation.append(elite_agent)
        
        # Generate rest through crossover and mutation
        while len(next_generation) < self.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1 = self._clone_agent(parent1)
                child2 = self._clone_agent(parent2)
            
            # Mutation
            child1 = self._mutate_agent(child1)
            child2 = self._mutate_agent(child2)
            
            # Update generation info
            child1.generation = self.current_generation + 1
            child2.generation = self.current_generation + 1
            child1.parent_ids = [parent1.agent_id, parent2.agent_id]
            child2.parent_ids = [parent1.agent_id, parent2.agent_id]
            
            next_generation.extend([child1, child2])
        
        return next_generation[:self.population_size]

    def _tournament_selection(self) -> AgentGenome:
        """Select an agent using tournament selection."""
        tournament_size = max(2, int(self.population_size * self.selection_pressure))
        return max(tournament_agents, key=lambda x: x.fitness_score)

    def _crossover(self, parent1: AgentGenome, parent2: AgentGenome) -> Tuple[AgentGenome, AgentGenome]:
        """Perform crossover between two parent agents."""
        # Create child agents
        child1 = self._clone_agent(parent1)
        child2 = self._clone_agent(parent2)
        
        # Crossover capabilities
        if random.random() < 0.5:
            child1.capabilities = self._crossover_lists(parent1.capabilities, parent2.capabilities)
            child2.capabilities = self._crossover_lists(parent2.capabilities, parent1.capabilities)
        
        # Crossover performance metrics
        for metric in child1.performance_metrics:
            if random.random() < 0.5:
                child1.performance_metrics[metric] = parent2.performance_metrics[metric]
                child2.performance_metrics[metric] = parent1.performance_metrics[metric]
        
        # Crossover other attributes
        if random.random() < 0.5:
            child1.learning_rate = parent2.learning_rate
            child2.learning_rate = parent1.learning_rate
        
        if random.random() < 0.5:
            child1.adaptation_threshold = parent2.adaptation_threshold
            child2.adaptation_threshold = parent1.adaptation_threshold
        
        return child1, child2

    def _crossover_lists(self, list1: List[str], list2: List[str]) -> List[str]:
        """Perform crossover on two lists."""
        # Take half from each parent
        half_size = len(list1) // 2
        result = list1[:half_size] + list2[half_size:]
        return list(set(result))  # Remove duplicates

    def _mutate_agent(self, agent: AgentGenome) -> AgentGenome:
        """Apply mutations to an agent."""
        if random.random() < agent.mutation_rate:
            # Mutate capabilities
            if random.random() < 0.3:
                agent.capabilities = self._mutate_capabilities(agent.capabilities)
            
            # Mutate performance metrics
            if random.random() < 0.3:
                for metric in agent.performance_metrics:
                    if random.random() < 0.5:
                        mutation = random.gauss(0, 0.1)
                        agent.performance_metrics[metric] = max(0.0, min(1.0, 
                            agent.performance_metrics[metric] + mutation))
            
            # Mutate learning rate
            if random.random() < 0.2:
                mutation = random.gauss(0, 0.01)
                agent.learning_rate = max(0.001, min(0.1, agent.learning_rate + mutation))
            
            # Mutate adaptation threshold
            if random.random() < 0.2:
                mutation = random.gauss(0, 0.05)
                agent.adaptation_threshold = max(0.1, min(0.9, 
                    agent.adaptation_threshold + mutation))
        
        return agent

    def _mutate_capabilities(self, capabilities: List[str]) -> List[str]:
        """Mutate agent capabilities."""
        all_capabilities = [
            "natural_language_processing", "computer_vision", "predictive_analytics",
            "pattern_recognition", "decision_making", "problem_solving",
            "creativity", "collaboration", "learning", "adaptation",
            "optimization", "reasoning", "memory", "attention",
            "planning", "execution", "monitoring", "evaluation"
        ]
        
        # Add or remove capabilities
        if random.random() < 0.5 and len(capabilities) > 3:
            # Remove a capability
            capabilities.remove(random.choice(capabilities))
        elif random.random() < 0.5 and len(capabilities) < 15:
            # Add a capability
            new_capability = random.choice([c for c in all_capabilities if c not in capabilities])
            capabilities.append(new_capability)
        
        return capabilities

    def _clone_agent(self, agent: AgentGenome) -> AgentGenome:
        """Create a deep copy of an agent."""
        return AgentGenome(
            agent_id=f"{agent.agent_id}_clone_{datetime.now().timestamp()}",
            agent_type=agent.agent_type,
            capabilities=agent.capabilities.copy(),
            performance_metrics=agent.performance_metrics.copy(),
            learning_rate=agent.learning_rate,
            adaptation_threshold=agent.adaptation_threshold,
            collaboration_preferences=agent.collaboration_preferences.copy(),
            mutation_rate=agent.mutation_rate,
            fitness_score=0.0,  # Reset fitness score
            generation=agent.generation,
            parent_ids=agent.parent_ids.copy(),
            created_at=datetime.now()
        )

    async def get_best_agents(self, count: int = 10) -> List[AgentGenome]:
        """Get the best performing agents."""
        sorted_agents = sorted(self.agent_population, key=lambda x: x.fitness_score, reverse=True)
        return sorted_agents[:count]

    async def get_agent_by_id(self, agent_id: str) -> Optional[AgentGenome]:
        for agent in self.agent_population:
            if agent.agent_id == agent_id:
                return agent
        return None

    def get_evolution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics."""
        if not self.evolution_history:
            return {"error": "No evolution history available"}
        
        recent_generations = self.evolution_history[-10:]  # Last 10 generations
        
        return {
            "current_generation": self.current_generation,
            "population_size": len(self.agent_population),
            "total_evolutions": len(self.evolution_history),
            "best_fitness_overall": max(gen["best_fitness"] for gen in self.evolution_history),
            "average_fitness_trend": [gen["average_fitness"] for gen in recent_generations],
            "fitness_improvement": self._calculate_fitness_improvement(),
            "diversity_metrics": self._calculate_diversity_metrics(),
            "convergence_status": self._check_convergence()
        }

    def _calculate_fitness_improvement(self) -> float:
        """Calculate overall fitness improvement."""
        if len(self.evolution_history) < 2:
            return 0.0
        
        initial_fitness = self.evolution_history[0]["average_fitness"]
        current_fitness = self.evolution_history[-1]["average_fitness"]
        return current_fitness - initial_fitness

    def _calculate_diversity_metrics(self) -> Dict[str, Any]:
        """Calculate population diversity metrics."""
        if not self.agent_population:
            return {"error": "No agents in population"}
        
        # Calculate capability diversity
        all_capabilities = set()
        for agent in self.agent_population:
            all_capabilities.update(agent.capabilities)
        
        capability_diversity = len(all_capabilities) / len(self.agent_population)
        
        # Calculate agent type distribution
        type_counts = {}
        for agent in self.agent_population:
            type_counts[agent.agent_type.value] = type_counts.get(agent.agent_type.value, 0) + 1
        
        return {
            "capability_diversity": capability_diversity,
            "agent_type_distribution": type_counts,
            "unique_capabilities": len(all_capabilities)
        }

    def _check_convergence(self) -> Dict[str, Any]:
        """Check if the population has converged."""
        if len(self.evolution_history) < 10:
            return {"converged": False, "reason": "Insufficient generations"}
        
        recent_fitness = [gen["average_fitness"] for gen in self.evolution_history[-10:]]
        fitness_variance = np.var(recent_fitness)
        
        return {
            "converged": fitness_variance < 0.01,
            "fitness_variance": fitness_variance,
            "generations_since_improvement": self._generations_since_improvement()
        }

    def _generations_since_improvement(self) -> int:
        """Calculate generations since last fitness improvement."""
        if len(self.evolution_history) < 2:
            return 0
        
        best_fitness = self.evolution_history[0]["best_fitness"]
        for i, gen in enumerate(self.evolution_history[1:], 1):
            if gen["best_fitness"] > best_fitness:
                best_fitness = gen["best_fitness"]
            else:
                return len(self.evolution_history) - i
        
        return 0

        try:
            # Find best base agent
            best_agents = await self.get_best_agents(5)
            base_agent = random.choice(best_agents)
            
            
            
            
            
            # Add to population
            

        except Exception as e:
            raise

    async def export_agent_genome(self, agent_id: str) -> Dict[str, Any]:
        """Export an agent's genome for external use."""
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type.value,
            "capabilities": agent.capabilities,
            "performance_metrics": agent.performance_metrics,
            "learning_rate": agent.learning_rate,
            "adaptation_threshold": agent.adaptation_threshold,
            "collaboration_preferences": agent.collaboration_preferences,
            "mutation_rate": agent.mutation_rate,
            "fitness_score": agent.fitness_score,
            "generation": agent.generation,
            "parent_ids": agent.parent_ids,
            "created_at": agent.created_at.isoformat()
        }

    async def import_agent_genome(self, genome_data: Dict[str, Any]) -> AgentGenome:
        """Import an agent genome from external source."""
        try:
            agent = AgentGenome(
                agent_id=genome_data["agent_id"],
                agent_type=AgentType(genome_data["agent_type"]),
                capabilities=genome_data["capabilities"],
                performance_metrics=genome_data["performance_metrics"],
                learning_rate=genome_data["learning_rate"],
                adaptation_threshold=genome_data["adaptation_threshold"],
                collaboration_preferences=genome_data["collaboration_preferences"],
                mutation_rate=genome_data["mutation_rate"],
                fitness_score=genome_data["fitness_score"],
                generation=genome_data["generation"],
                parent_ids=genome_data["parent_ids"],
                created_at=datetime.fromisoformat(genome_data["created_at"])
            )
            
            self.agent_population.append(agent)
            logger.info(f"✅ Imported agent genome: {agent.agent_id}")
            return agent

        except Exception as e:
            logger.error(f"Failed to import agent genome: {e}")
            raise
