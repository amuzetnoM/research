#!/usr/bin/env python3
"""
Error Testing Tool for AI Research Environment

This script provides utilities to test various error handling mechanisms
in the research environment and collect metrics on their effectiveness.
"""

import os
import sys
import time
import json
import random
import logging
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple, Union, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('error_testing')

# Try to import environment-specific modules
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.diagnostics import handle_exception, ResourceError, ConfigurationError, NetworkError
    from utils.system_utils import system_manager
    INTERNAL_MODULES_AVAILABLE = True
except ImportError:
    logger.warning("Could not import internal modules. Running in standalone mode.")
    INTERNAL_MODULES_AVAILABLE = False
    
    # Define minimal versions for standalone operation
    class CustomError(Exception):
        pass
        
    class ResourceError(CustomError):
        pass
        
    class ConfigurationError(CustomError):
        pass
        
    class NetworkError(CustomError):
        pass
    
    def handle_exception(message, exception=None, exit_code=None, notify=False):
        logger.error(f"{message}: {exception}")


class ErrorTestingFramework:
    """Framework for testing error handling mechanisms and measuring their effectiveness."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the testing framework.
        
        Args:
            config_path: Path to configuration file with test scenarios
        """
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
        self.test_count = 0
        self.success_count = 0
        
        # Load configuration if provided
        self.config = self._load_config(config_path) if config_path else self._default_config()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load test configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return self._default_config()
            
    def _default_config(self) -> Dict:
        """Return default test configuration."""
        return {
            "test_scenarios": [
                {
                    "name": "resource_errors",
                    "description": "Test handling of resource exhaustion errors",
                    "iterations": 20,
                    "concurrency": 2,
                    "error_type": "resource"
                },
                {
                    "name": "network_errors",
                    "description": "Test handling of network connectivity issues",
                    "iterations": 20, 
                    "concurrency": 2,
                    "error_type": "network"
                },
                {
                    "name": "configuration_errors",
                    "description": "Test handling of configuration issues",
                    "iterations": 20,
                    "concurrency": 1,
                    "error_type": "config"
                }
            ],
            "output_path": "logs/error_test_results.json"
        }
    
    def run_tests(self) -> Dict:
        """Run all test scenarios and collect results."""
        logger.info(f"Starting error handling tests with {len(self.config['test_scenarios'])} scenarios")
        
        for scenario in self.config["test_scenarios"]:
            self._run_scenario(scenario)
            
        # Calculate summary metrics
        total_time = (datetime.now() - self.start_time).total_seconds()
        success_rate = (self.success_count / self.test_count) * 100 if self.test_count > 0 else 0
        
        summary = {
            "total_tests": self.test_count,
            "successful_tests": self.success_count,
            "success_rate": f"{success_rate:.2f}%",
            "total_time": f"{total_time:.2f}s",
            "scenarios": len(self.config['test_scenarios']),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save detailed results
        self.results["summary"] = summary
        self._save_results()
        
        logger.info(f"Testing complete: {self.success_count}/{self.test_count} tests passed ({success_rate:.2f}%)")
        return self.results
    
    def _run_scenario(self, scenario: Dict) -> None:
        """Run a specific test scenario."""
        name = scenario["name"]
        iterations = scenario.get("iterations", 10)
        concurrency = scenario.get("concurrency", 1)
        error_type = scenario.get("error_type", "generic")
        
        logger.info(f"Running scenario '{name}': {iterations} iterations with concurrency {concurrency}")
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for i in range(iterations):
                futures.append(executor.submit(self._run_test_case, error_type, i))
            
            for future in futures:
                result = future.result()
                results.append(result)
                self.test_count += 1
                if result["success"]:
                    self.success_count += 1
        
        scenario_time = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / len(results)) * 100 if results else 0
        
        self.results[name] = {
            "description": scenario.get("description", ""),
            "results": results,
            "success_rate": f"{success_rate:.2f}%",
            "execution_time": f"{scenario_time:.2f}s",
            "success_count": success_count,
            "total_tests": len(results)
        }
        
        logger.info(f"Scenario '{name}' completed: {success_count}/{len(results)} tests passed ({success_rate:.2f}%)")
    
    def _run_test_case(self, error_type: str, test_index: int) -> Dict:
        """Run a single test case simulating a specific error type."""
        test_id = f"{error_type}_{test_index}"
        start_time = time.time()
        success = False
        error_message = ""
        error_details = {}
        
        try:
            # Simulate different types of errors
            if error_type == "resource":
                self._simulate_resource_error()
            elif error_type == "network":
                self._simulate_network_error()
            elif error_type == "config":
                self._simulate_config_error()
            else:
                self._simulate_generic_error()
                
            # If we get here, error wasn't properly raised
            success = False
            error_message = "Failed to simulate error correctly"
            
        except Exception as e:
            # A correctly handled error should be caught and not propagate here
            if isinstance(e, (ResourceError, NetworkError, ConfigurationError, CustomError)):
                # These errors should have been handled properly
                success = True
            else:
                # Unexpected error type
                success = False
                error_message = f"Unexpected error: {type(e).__name__}: {e}"
            
            error_details = {
                "type": type(e).__name__,
                "message": str(e)
            }
        
        execution_time = time.time() - start_time
        
        return {
            "test_id": test_id,
            "success": success,
            "execution_time": f"{execution_time:.4f}s",
            "error_message": error_message,
            "error_details": error_details,
            "timestamp": datetime.now().isoformat()
        }
    
    def _simulate_resource_error(self) -> None:
        """Simulate a resource error (memory, CPU, disk)."""
        error_types = ["memory", "cpu", "disk"]
        error_type = random.choice(error_types)
        
        if error_type == "memory":
            try:
                # Try to allocate a large array
                large_array = [0] * (10**8)  # Approx 800MB
                # If successful, raise a simulated memory error
                raise ResourceError("Simulated out of memory error")
            except MemoryError:
                # Handle real memory error
                handle_exception("Out of memory during test", MemoryError("Allocation failed"))
                raise ResourceError("Actual memory allocation failed")
        
        elif error_type == "cpu":
            # Simulate CPU overload
            raise ResourceError("Simulated CPU overload")
        
        else:  # disk
            # Simulate disk space issue
            raise ResourceError("Simulated disk space exhaustion")
    
    def _simulate_network_error(self) -> None:
        """Simulate network connectivity issues."""
        error_subtypes = ["timeout", "connection_refused", "dns_failure"]
        subtype = random.choice(error_subtypes)
        
        raise NetworkError(f"Simulated network error: {subtype}")
    
    def _simulate_config_error(self) -> None:
        """Simulate configuration errors."""
        error_subtypes = ["missing_key", "invalid_value", "type_mismatch"]
        subtype = random.choice(error_subtypes)
        
        raise ConfigurationError(f"Simulated configuration error: {subtype}")
    
    def _simulate_generic_error(self) -> None:
        """Simulate a generic error."""
        raise Exception("Simulated generic error")
    
    def _save_results(self) -> None:
        """Save test results to file."""
        output_path = self.config.get("output_path", "logs/error_test_results.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results to {output_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Test error handling mechanisms in the research environment')
    parser.add_argument('--config', '-c', help='Path to test configuration file')
    parser.add_argument('--output', '-o', help='Path to save test results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    config = None
    if args.config:
        config = args.config
    
    framework = ErrorTestingFramework(config)
    
    if args.output:
        framework.config["output_path"] = args.output
    
    framework.run_tests()


if __name__ == "__main__":
    main()
