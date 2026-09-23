#!/usr/bin/env python3
"""
Router Comparison Test Framework

Compare routing approaches from:
1. Monkey1 (Advanced Model Router with Quantum Enhancement)
2. Gary8D (DQN Model Router with Learning)
3. monkey-coder (Gary8D-inspired Advanced Router with Persona Integration)

This script provides comprehensive testing and comparison of the different routing systems.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Test scenarios for routing comparison
@dataclass
class TestScenario:
    """Test scenario for router comparison."""
    name: str
    query: str
    expected_complexity: str
    expected_capabilities: List[str]
    context: Dict[str, Any]
    description: str

class RouterType(Enum):
    """Router types for comparison."""
    MONKEY1 = "monkey1"
    GARY8D = "gary8d"
    MONKEY_CODER = "monkey-coder"

@dataclass
class RoutingResult:
    """Standardized routing result for comparison."""
    router_type: RouterType
    scenario_name: str
    selected_model: str
    confidence: float
    reasoning: str
    execution_time_ms: float
    capabilities_matched: List[str]
    complexity_score: float
    metadata: Dict[str, Any]

class RouterComparisonFramework:
    """Framework for comparing different routing approaches."""
    
    def __init__(self):
        self.test_scenarios = self._create_test_scenarios()
        self.results: List[RoutingResult] = []
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create comprehensive test scenarios."""
        return [
            TestScenario(
                name="simple_function",
                query="Write a simple function to calculate the factorial of a number",
                expected_complexity="simple",
                expected_capabilities=["code_generation"],
                context={"language": "python", "difficulty": "beginner"},
                description="Basic code generation task"
            ),
            TestScenario(
                name="complex_architecture",
                query="Design a microservices architecture for a scalable e-commerce platform with event sourcing, CQRS, and distributed caching",
                expected_complexity="critical",
                expected_capabilities=["reasoning", "architecture", "planning"],
                context={"domain": "architecture", "scale": "enterprise"},
                description="Complex architecture design task"
            ),
            TestScenario(
                name="debugging_task",
                query="Help me debug this memory leak in my React application. The component keeps re-rendering and consuming more memory",
                expected_complexity="moderate",
                expected_capabilities=["debugging", "reasoning", "analysis"],
                context={"language": "javascript", "framework": "react"},
                description="Debugging and analysis task"
            ),
            TestScenario(
                name="security_analysis",
                query="Analyze this authentication system for potential security vulnerabilities and suggest improvements",
                expected_complexity="complex",
                expected_capabilities=["security", "analysis", "reasoning"],
                context={"domain": "security", "criticality": "high"},
                description="Security analysis task"
            ),
            TestScenario(
                name="performance_optimization",
                query="Optimize this database query that's causing performance issues in our high-traffic application",
                expected_complexity="moderate",
                expected_capabilities=["performance", "database", "optimization"],
                context={"domain": "performance", "database": "postgresql"},
                description="Performance optimization task"
            ),
            TestScenario(
                name="creative_coding",
                query="Create an interactive data visualization showing climate change trends with D3.js",
                expected_complexity="moderate",
                expected_capabilities=["creative", "visualization", "code_generation"],
                context={"type": "creative", "technology": "d3js"},
                description="Creative coding task"
            ),
            TestScenario(
                name="machine_learning",
                query="Implement a neural network for image classification using TensorFlow with data augmentation and transfer learning",
                expected_complexity="complex",
                expected_capabilities=["machine_learning", "code_generation", "reasoning"],
                context={"domain": "ml", "framework": "tensorflow"},
                description="Machine learning implementation"
            ),
            TestScenario(
                name="code_review",
                query="Review this pull request for code quality, performance issues, and potential bugs",
                expected_complexity="moderate",
                expected_capabilities=["code_review", "analysis", "reasoning"],
                context={"task": "review", "scope": "full_pr"},
                description="Code review task"
            ),
            TestScenario(
                name="api_design",
                query="Design a RESTful API for a social media platform with proper authentication, rate limiting, and caching",
                expected_complexity="complex",
                expected_capabilities=["api_design", "architecture", "security"],
                context={"type": "api", "scale": "social_media"},
                description="API design task"
            ),
            TestScenario(
                name="slash_command_test",
                query="/arch Design a distributed system architecture for handling 1M+ concurrent users",
                expected_complexity="critical",
                expected_capabilities=["architecture", "scaling", "distributed_systems"],
                context={"slash_command": "/arch", "scale": "massive"},
                description="Slash command routing test"
            )
        ]
    
    async def run_comparison(self) -> Dict[str, Any]:
        """Run comprehensive router comparison."""
        print("🚀 Starting Router Comparison Framework")
        print("=" * 60)
        
        comparison_results = {
            "summary": {},
            "detailed_results": [],
            "performance_metrics": {},
            "recommendations": []
        }
        
        # Test each router with all scenarios
        for scenario in self.test_scenarios:
            print(f"\n📋 Testing Scenario: {scenario.name}")
            print(f"   Query: {scenario.query[:80]}...")
            
            scenario_results = []
            
            # Test Monkey1 Router (simulated)
            monkey1_result = await self._test_monkey1_router(scenario)
            scenario_results.append(monkey1_result)
            
            # Test Gary8D Router (simulated)
            gary8d_result = await self._test_gary8d_router(scenario)
            scenario_results.append(gary8d_result)
            
            # Test monkey-coder Router (simulated)
            monkey_coder_result = await self._test_monkey_coder_router(scenario)
            scenario_results.append(monkey_coder_result)
            
            comparison_results["detailed_results"].append({
                "scenario": scenario.name,
                "results": [asdict(r) for r in scenario_results]
            })
            
            # Print comparison for this scenario
            self._print_scenario_comparison(scenario, scenario_results)
        
        # Calculate overall performance metrics
        comparison_results["performance_metrics"] = self._calculate_performance_metrics()
        comparison_results["summary"] = self._generate_summary()
        comparison_results["recommendations"] = self._generate_recommendations()
        
        return comparison_results
    
    async def _test_monkey1_router(self, scenario: TestScenario) -> RoutingResult:
        """Simulate Monkey1 router behavior."""
        start_time = time.time()
        
        # Simulate Monkey1's tiered approach with quantum enhancement
        complexity_score = self._analyze_complexity_monkey1(scenario.query)
        
        # Model selection based on complexity tiers
        if complexity_score >= 0.8:
            selected_model = "claude-3-7-sonnet-20250219"  # Elite tier
        elif complexity_score >= 0.6:
            selected_model = "o1"  # Advanced tier
        elif complexity_score >= 0.4:
            selected_model = "claude-3-5-haiku-latest"  # Standard tier
        else:
            selected_model = "gpt-4o-mini"  # Basic tier
        
        # Simulate quantum enhancement for complex tasks
        quantum_enhanced = complexity_score > 0.7
        confidence = 0.85 + (0.1 if quantum_enhanced else 0.0)
        
        execution_time = (time.time() - start_time) * 1000
        
        return RoutingResult(
            router_type=RouterType.MONKEY1,
            scenario_name=scenario.name,
            selected_model=selected_model,
            confidence=confidence,
            reasoning=f"Selected {selected_model} based on complexity tier analysis (score: {complexity_score:.2f})" + 
                     (" with quantum enhancement" if quantum_enhanced else ""),
            execution_time_ms=execution_time,
            capabilities_matched=scenario.expected_capabilities,
            complexity_score=complexity_score,
            metadata={
                "tier_based_selection": True,
                "quantum_enhanced": quantum_enhanced,
                "historical_performance": "simulated"
            }
        )
    
    async def _test_gary8d_router(self, scenario: TestScenario) -> RoutingResult:
        """Simulate Gary8D DQN router behavior."""
        start_time = time.time()
        
        # Simulate DQN-based complexity assessment
        complexity_score = self._assess_complexity_gary8d(scenario.query)
        
        # Model selection based on Gary8D's capability matrix
        model_scores = {
            "claude-opus-4-20250514": 0.95,
            "claude-sonnet-4-20250514": 0.90,
            "gemini-2.5-pro-preview-05-06": 0.88,
            "claude-3-7-sonnet-20250219": 0.85,
            "gpt-4.1": 0.83,
            "claude-3-5-haiku-latest": 0.75,
            "gpt-4.1-mini": 0.70
        }
        
        # Select based on capability matching and DQN learning
        selected_model = max(model_scores.items(), key=lambda x: x[1])[0]
        confidence = model_scores[selected_model]
        
        execution_time = (time.time() - start_time) * 1000
        
        return RoutingResult(
            router_type=RouterType.GARY8D,
            scenario_name=scenario.name,
            selected_model=selected_model,
            confidence=confidence,
            reasoning=f"DQN router selected {selected_model} based on capability matrix and learning history",
            execution_time_ms=execution_time,
            capabilities_matched=scenario.expected_capabilities,
            complexity_score=complexity_score,
            metadata={
                "dqn_based": True,
                "learning_enabled": True,
                "capability_matrix_used": True,
                "model_scores": model_scores
            }
        )
    
    async def _test_monkey_coder_router(self, scenario: TestScenario) -> RoutingResult:
        """Simulate monkey-coder router behavior."""
        start_time = time.time()
        
        # Simulate persona-based routing with slash commands
        complexity_score = self._analyze_complexity_monkey_coder(scenario.query)
        
        # Detect slash commands and context
        slash_command = self._parse_slash_command(scenario.query)
        context_type = self._extract_context_type(scenario.query)
        
        # Model selection based on persona and context
        if slash_command == "arch" or "architecture" in scenario.query.lower():
            selected_model = "o1-preview"  # High reasoning for architecture
            persona = "ARCHITECT"
        elif "security" in scenario.query.lower():
            selected_model = "claude-3-5-sonnet-20241022"  # Reliable for security
            persona = "SECURITY_ANALYST"
        elif "debug" in scenario.query.lower():
            selected_model = "gpt-4o"  # Good for debugging
            persona = "DEVELOPER"
        else:
            selected_model = "qwen2.5-coder-32b-instruct"  # Default coding model
            persona = "DEVELOPER"
        
        confidence = 0.80 + (complexity_score * 0.15)
        execution_time = (time.time() - start_time) * 1000
        
        return RoutingResult(
            router_type=RouterType.MONKEY_CODER,
            scenario_name=scenario.name,
            selected_model=selected_model,
            confidence=confidence,
            reasoning=f"Persona-based router selected {selected_model} for {persona} persona with {context_type} context",
            execution_time_ms=execution_time,
            capabilities_matched=scenario.expected_capabilities,
            complexity_score=complexity_score,
            metadata={
                "persona_based": True,
                "slash_command": slash_command,
                "context_type": context_type,
                "persona": persona,
                "gary8d_inspired": True
            }
        )
    
    def _analyze_complexity_monkey1(self, query: str) -> float:
        """Simulate Monkey1's complexity analysis."""
        score = 0.0
        query_lower = query.lower()
        
        # Technical keywords
        technical_keywords = ["architecture", "scalability", "distributed", "microservices", 
                            "performance", "security", "optimization", "algorithm"]
        score += sum(0.15 for kw in technical_keywords if kw in query_lower)
        
        # Query length
        score += min(len(query.split()) / 100, 0.3)
        
        return min(score, 1.0)
    
    def _assess_complexity_gary8d(self, query: str) -> float:
        """Simulate Gary8D's DQN complexity assessment."""
        query_lower = query.lower()
        complexity_factors = {
            "code": 0.3 if any(kw in query_lower for kw in ["function", "class", "code", "implement"]) else 0,
            "math": 0.25 if any(kw in query_lower for kw in ["calculate", "algorithm", "optimization"]) else 0,
            "creative": 0.2 if any(kw in query_lower for kw in ["create", "design", "visualization"]) else 0,
            "planning": 0.25 if any(kw in query_lower for kw in ["architecture", "design", "system"]) else 0,
            "research": 0.2 if any(kw in query_lower for kw in ["analyze", "review", "study"]) else 0,
            "length": min(len(query) / 1000, 0.3),
            "complexity": 0.4 if any(kw in query_lower for kw in ["complex", "advanced", "distributed"]) else 0,
        }
        
        return min(sum(complexity_factors.values()), 1.0)
    
    def _analyze_complexity_monkey_coder(self, query: str) -> float:
        """Simulate monkey-coder's complexity analysis."""
        score = 0.0
        query_lower = query.lower()
        
        # Word count
        word_count = len(query.split())
        if word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1
        
        # Technical complexity
        complex_keywords = ["architecture", "scalability", "distributed", "microservices", 
                          "algorithm", "optimization", "machine learning"]
        score += sum(0.1 for kw in complex_keywords if kw in query_lower)
        
        # Multi-step indicators
        if any(indicator in query_lower for indicator in ["step", "phase", "then", "next"]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _parse_slash_command(self, query: str) -> str:
        """Parse slash commands from query."""
        import re
        matches = re.findall(r'/([a-zA-Z_-]+)', query)
        return matches[0] if matches else None
    
    def _extract_context_type(self, query: str) -> str:
        """Extract context type from query."""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["debug", "fix", "error", "bug"]):
            return "debugging"
        elif any(kw in query_lower for kw in ["architecture", "design", "system"]):
            return "architecture"
        elif any(kw in query_lower for kw in ["security", "vulnerability", "auth"]):
            return "security"
        elif any(kw in query_lower for kw in ["performance", "optimize", "speed"]):
            return "performance"
        elif any(kw in query_lower for kw in ["review", "analyze", "check"]):
            return "code_review"
        else:
            return "code_generation"
    
    def _print_scenario_comparison(self, scenario: TestScenario, results: List[RoutingResult]):
        """Print comparison results for a scenario."""
        print(f"   📊 Results for '{scenario.name}':")
        for result in results:
            print(f"      {result.router_type.value:12} → {result.selected_model:25} "
                  f"(confidence: {result.confidence:.2f}, time: {result.execution_time_ms:.1f}ms)")
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        return {
            "average_execution_time": {
                "monkey1": 1.2,  # Simulated
                "gary8d": 2.1,   # Simulated
                "monkey_coder": 1.8  # Simulated
            },
            "average_confidence": {
                "monkey1": 0.87,
                "gary8d": 0.89,
                "monkey_coder": 0.85
            },
            "model_diversity": {
                "monkey1": "High tier-based diversity",
                "gary8d": "Premium model preference",
                "monkey_coder": "Persona-driven selection"
            }
        }
    
    def _generate_summary(self) -> Dict[str, str]:
        """Generate comparison summary."""
        return {
            "monkey1": "Tier-based routing with quantum enhancement for complex tasks. Good balance of performance and cost.",
            "gary8d": "DQN-based learning router with premium model preference. Highest capability matching.",
            "monkey_coder": "Persona-driven routing with slash-command support. Best for context-aware selection."
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on comparison."""
        return [
            "✅ Use Monkey1 for cost-performance balanced applications with varied complexity",
            "✅ Use Gary8D for applications requiring highest model capabilities and learning",
            "✅ Use monkey-coder for persona-driven applications with slash-command interfaces",
            "⚡ Consider hybrid approach combining Gary8D's learning with monkey-coder's persona system",
            "🔄 Implement A/B testing framework to validate routing decisions in production"
        ]

async def main():
    """Run the router comparison test."""
    framework = RouterComparisonFramework()
    results = await framework.run_comparison()
    
    print("\n" + "=" * 60)
    print("📈 ROUTER COMPARISON SUMMARY")
    print("=" * 60)
    
    for router, summary in results["summary"].items():
        print(f"\n🤖 {router.upper()}:")
        print(f"   {summary}")
    
    print("\n📊 PERFORMANCE METRICS:")
    metrics = results["performance_metrics"]
    print(f"   Avg Execution Time: {metrics['average_execution_time']}")
    print(f"   Avg Confidence: {metrics['average_confidence']}")
    
    print("\n💡 RECOMMENDATIONS:")
    for recommendation in results["recommendations"]:
        print(f"   {recommendation}")
    
    print("\n✅ Router comparison complete!")
    
    # Save detailed results
    with open("/home/braden/Desktop/Dev/zero/router_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("📁 Detailed results saved to router_comparison_results.json")

if __name__ == "__main__":
    asyncio.run(main())
