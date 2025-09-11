#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Circuit Breaker Pattern Implementation
====================================

Circuit breaker for system resilience:
- Open circuit after consecutive failures
- Half-open state for testing recovery
- Automatic recovery detection
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict
from enum import Enum
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 10,
                 recovery_timeout: int = 300,
                 success_threshold: int = 3,
                 name: str = "CircuitBreaker"):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Time in seconds before attempting to close circuit
            success_threshold: Number of consecutive successes needed to close circuit from half-open
            name: Name of the circuit breaker for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.name = name
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'circuit_opened_count': 0,
            'circuit_closed_count': 0,
            'circuit_half_open_count': 0
        }
        
        logger.info(f"Circuit breaker '{name}' initialized with failure threshold {failure_threshold}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenException: When circuit is open
            Exception: When function execution fails
        """
        with self.lock:
            self.stats['total_calls'] += 1
            
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self.stats['circuit_half_open_count'] += 1
                    logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Last failure: {self.last_failure_time}. "
                        f"Will retry after: {self.recovery_timeout} seconds"
                    )
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution"""
        self.last_success_time = time.time()
        self.success_count += 1
        self.failure_count = 0
        self.stats['successful_calls'] += 1
        
        # If in half-open state and enough successes, close circuit
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.stats['circuit_closed_count'] += 1
                logger.info(f"Circuit breaker '{self.name}' moved to CLOSED state after {self.success_count} successes")
    
    def _on_failure(self):
        """Handle failed execution"""
        self.last_failure_time = time.time()
        self.failure_count += 1
        self.success_count = 0
        self.stats['failed_calls'] += 1
        
        # If failure threshold reached, open circuit
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.stats['circuit_opened_count'] += 1
            logger.warning(f"Circuit breaker '{self.name}' moved to OPEN state after {self.failure_count} failures")
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'last_success_time': self.last_success_time,
                'stats': self.stats.copy()
            }
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_success_time = None
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED state")
    
    def is_available(self) -> bool:
        """Check if circuit breaker allows calls"""
        return self.state != CircuitState.OPEN

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self.breakers = {}
        self.lock = threading.Lock()
    
    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker by name"""
        with self.lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(name=name, **kwargs)
            return self.breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        with self.lock:
            return {name: breaker.get_stats() for name, breaker in self.breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers"""
        with self.lock:
            for breaker in self.breakers.values():
                breaker.reset()
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all circuit breakers"""
        all_stats = self.get_all_stats()
        
        total_calls = sum(stats['stats']['total_calls'] for stats in all_stats.values())
        total_successful = sum(stats['stats']['successful_calls'] for stats in all_stats.values())
        total_failed = sum(stats['stats']['failed_calls'] for stats in all_stats.values())
        
        open_circuits = sum(1 for stats in all_stats.values() if stats['state'] == 'OPEN')
        half_open_circuits = sum(1 for stats in all_stats.values() if stats['state'] == 'HALF_OPEN')
        closed_circuits = sum(1 for stats in all_stats.values() if stats['state'] == 'CLOSED')
        
        return {
            'total_breakers': len(self.breakers),
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'closed_circuits': closed_circuits,
            'total_calls': total_calls,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': (total_successful / total_calls * 100) if total_calls > 0 else 0
        }

# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()

def circuit_breaker(name: str, **kwargs):
    """Decorator for circuit breaker protection"""
    def decorator(func):
        def wrapper(*args, **kwargs_inner):
            breaker = circuit_manager.get_breaker(name, **kwargs)
            return breaker.call(func, *args, **kwargs_inner)
        return wrapper
    return decorator

def main():
    """Example usage"""
    print("🔌 Circuit Breaker Pattern Implementation")
    print("=" * 50)
    
    # Create a circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=10,
        success_threshold=2,
        name="ExampleBreaker"
    )
    
    # Example function that might fail
    def unreliable_function(success_rate: float = 0.7):
        import random
        if random.random() < success_rate:
            return "Success!"
        else:
            raise Exception("Random failure")
    
    # Test circuit breaker
    print("Testing circuit breaker with unreliable function...")
    
    for i in range(10):
        try:
            result = breaker.call(unreliable_function, success_rate=0.3)
            print(f"Call {i+1}: {result}")
        except CircuitBreakerOpenException as e:
            print(f"Call {i+1}: Circuit breaker is OPEN - {e}")
        except Exception as e:
            print(f"Call {i+1}: Function failed - {e}")
        
        # Show state
        stats = breaker.get_stats()
        print(f"  State: {stats['state']}, Failures: {stats['failure_count']}, Successes: {stats['success_count']}")
        print()
    
    # Show final statistics
    print("Final Statistics:")
    stats = breaker.get_stats()
    for key, value in stats['stats'].items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
