"""
Comparison engine for analyzing test case similarities with Context Engineering
"""
import os
import sys
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import AzureOpenAI
from config.config import Config
from core.models import TestCase, ComparisonResult, DecisionType
from engines.embeddings import EmbeddingGenerator
from engines.context_engineering import ContextEngineer
from core.utils import load_json
import json


class ComparisonEngine:
    """Compare test cases to determine relationships using advanced context engineering"""
    
    def __init__(self, use_context_engineering: bool = True):
        """
        Initialize comparison engine
        
        Args:
            use_context_engineering: Enable advanced context engineering techniques
        """
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        self.embedding_generator = EmbeddingGenerator()
        self.prompts = load_json("prompts.json")
        self.use_context_engineering = use_context_engineering
        
        # Initialize context engineer if enabled
        if self.use_context_engineering:
            self.context_engineer = ContextEngineer()
    
    def compare_test_cases(
        self, 
        new_test_case: TestCase, 
        existing_test_case: TestCase,
        historical_decisions: Optional[List[Dict]] = None
    ) -> ComparisonResult:
        """
        Compare two test cases using hybrid semantic + LLM similarity
        
        This method combines:
        1. Semantic similarity (via embeddings) - Fast mathematical comparison
        2. LLM deep analysis - Contextual understanding of business rules
        3. Hybrid score - Weighted combination for robust decision-making
        
        Args:
            new_test_case: New test case to compare
            existing_test_case: Existing test case from knowledge base
            
        Returns:
            ComparisonResult with decision and analysis
        """
        # Step 1: Calculate semantic similarity (embedding-based)
        new_embedding = self.embedding_generator.generate_embedding(
            new_test_case.to_text()
        )
        existing_embedding = self.embedding_generator.generate_embedding(
            existing_test_case.to_text()
        )
        semantic_similarity = self.embedding_generator.calculate_similarity(
            new_embedding, existing_embedding
        )
        
        # Step 2: Use LLM for deep contextual analysis
        analysis = self._analyze_with_llm(new_test_case, existing_test_case)
        
        # Step 3: Calculate LLM-based similarity score
        llm_similarity = self._calculate_llm_similarity(analysis)
        
        # Step 4: Compute hybrid similarity score (weighted combination)
        # Semantic: 60% weight (fast, reliable for exact matches)
        # LLM: 40% weight (contextual, catches semantic equivalence)
        hybrid_similarity = (
            Config.SEMANTIC_WEIGHT * semantic_similarity +
            Config.LLM_WEIGHT * llm_similarity
        )
        
        # Step 5: Determine decision based on hybrid score and analysis
        decision = self._make_decision(
            hybrid_similarity, 
            semantic_similarity,
            analysis
        )
        
        # Step 6: Generate human-readable reasoning
        reasoning = self._generate_reasoning(
            decision, 
            hybrid_similarity,
            semantic_similarity,
            llm_similarity,
            analysis
        )
        
        # Step 7: Calculate confidence score
        confidence_score = self._calculate_confidence(
            hybrid_similarity,
            semantic_similarity,
            llm_similarity,
            analysis
        )
        
        return ComparisonResult(
            new_test_case_id=new_test_case.id,
            existing_test_case_id=existing_test_case.id,
            similarity_score=hybrid_similarity,  # Use hybrid score as primary
            decision=decision,
            reasoning=reasoning,
            business_rule_match=analysis.get("business_rule_match", False),
            behavior_match=analysis.get("behavior_match", False),
            coverage_expansion=analysis.get("coverage_expansion", []),
            confidence_score=confidence_score
        )
    
    def _analyze_with_llm(
        self, 
        new_test_case: TestCase, 
        existing_test_case: TestCase,
        historical_decisions: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze test case relationship with context engineering
        
        Args:
            new_test_case: New test case
            existing_test_case: Existing test case
            historical_decisions: Similar past decisions for learning
            
        Returns:
            Analysis dictionary
        """
        # Use context engineering if enabled
        if self.use_context_engineering and hasattr(self, 'context_engineer'):
            # Calculate semantic similarity for context
            new_embedding = self.embedding_generator.generate_embedding(new_test_case.to_text())
            existing_embedding = self.embedding_generator.generate_embedding(existing_test_case.to_text())
            semantic_similarity = self.embedding_generator.calculate_similarity(new_embedding, existing_embedding)
            
            # Enhance prompts with context engineering
            enhanced_prompts = self.context_engineer.enhance_comparison_prompt(
                new_test_case=new_test_case,
                existing_test_case=existing_test_case,
                similarity_score=semantic_similarity,
                historical_decisions=historical_decisions
            )
            system_prompt = enhanced_prompts["system"]
            user_prompt = enhanced_prompts["user"]
        else:
            # Use basic prompts
            system_prompt = self.prompts["comparison_analysis"]["system"]
            user_prompt = self.prompts["comparison_analysis"]["user"].format(
                new_test_case=new_test_case.model_dump_json(indent=2),
                existing_test_case=existing_test_case.model_dump_json(indent=2)
            )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            # Extract JSON - handle different formatting scenarios
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Clean up the JSON string - remove extra whitespace and newlines within quotes
            import re
            # Remove newlines and extra spaces within the JSON structure
            content = re.sub(r'\s+', ' ', content)
            # Fix common JSON issues
            content = content.replace('\\n', ' ').replace('\n', ' ')
            
            # Try to parse JSON
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError as je:
                print(f"JSON parsing error: {je}")
                print(f"Problematic content: {content[:200]}...")
                # Try to extract key-value pairs manually as fallback
                analysis = {
                    "business_rule_match": "true" in content.lower() and "business_rule_match" in content,
                    "behavior_match": "true" in content.lower() and "behavior_match" in content, 
                    "coverage_expansion": [],
                    "relationship": "different",
                    "reasoning": "Analysis completed with fallback parsing"
                }
            
            # Ensure all required fields exist
            required_fields = {
                "business_rule_match": False,
                "behavior_match": False,
                "coverage_expansion": [],
                "relationship": "different",
                "reasoning": "Analysis completed"
            }
            for field, default in required_fields.items():
                if field not in analysis:
                    analysis[field] = default
            
            return analysis
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            import traceback
            traceback.print_exc()
            # Return default analysis
            return {
                "business_rule_match": False,
                "behavior_match": False,
                "coverage_expansion": [],
                "relationship": "different",
                "reasoning": f"Error in analysis: {str(e)[:100]}"
            }
    
    def _calculate_llm_similarity(self, analysis: Dict[str, Any]) -> float:
        """
        Convert LLM analysis to a numerical similarity score
        
        This provides a complementary similarity metric based on
        semantic understanding rather than just embedding distance.
        
        Args:
            analysis: LLM analysis results
            
        Returns:
            LLM-based similarity score (0.0 - 1.0)
        """
        # Base score from relationship type
        relationship = analysis.get("relationship", "different")
        relationship_scores = {
            "identical": 1.0,
            "expanded": 0.75,
            "similar": 0.60,
            "related": 0.45,
            "different": 0.20
        }
        base_score = relationship_scores.get(relationship, 0.20)
        
        # Boost for business rule and behavior matches
        business_rule_match = analysis.get("business_rule_match", False)
        behavior_match = analysis.get("behavior_match", False)
        
        # Calculate boosted score
        llm_score = base_score
        if business_rule_match:
            llm_score = min(llm_score + 0.15, 1.0)
        if behavior_match:
            llm_score = min(llm_score + 0.10, 1.0)
        
        return llm_score
    
    def _make_decision(
        self, 
        hybrid_similarity: float,
        semantic_similarity: float,
        analysis: Dict[str, Any]
    ) -> DecisionType:
        """
        Make decision using hybrid similarity score and analysis
        
        Args:
            hybrid_similarity: Combined semantic + LLM similarity score
            semantic_similarity: Pure embedding-based similarity
            analysis: LLM analysis results
            
        Returns:
            Decision type
        """
        business_rule_match = analysis.get("business_rule_match", False)
        behavior_match = analysis.get("behavior_match", False)
        relationship = analysis.get("relationship", "different")
        coverage_expansion = analysis.get("coverage_expansion", [])
        
        # SAME: High hybrid similarity + matching business rule + identical behavior
        # Use hybrid score for primary decision but verify with semantic baseline
        if (hybrid_similarity >= Config.THRESHOLD_SAME and 
            semantic_similarity >= Config.THRESHOLD_SAME - 0.05 and  # Allow 5% tolerance
            business_rule_match and 
            behavior_match and
            relationship == "identical"):
            return DecisionType.SAME
        
        # ADD-ON: Medium-high hybrid similarity + same business rule + expanded coverage
        if (Config.THRESHOLD_ADDON_MIN <= hybrid_similarity < Config.THRESHOLD_SAME and
            business_rule_match and
            (relationship == "expanded" or len(coverage_expansion) > 0)):
            return DecisionType.ADDON
        
        # Special case: Very high similarity but with coverage expansion
        # (e.g., same test case with additional edge cases)
        if (hybrid_similarity >= Config.THRESHOLD_SAME and
            business_rule_match and
            len(coverage_expansion) > 0):
            return DecisionType.ADDON
        
        # NEW: Low similarity or different business rule
        return DecisionType.NEW
    
    def _generate_reasoning(
        self, 
        decision: DecisionType, 
        hybrid_similarity: float,
        semantic_similarity: float,
        llm_similarity: float,
        analysis: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable reasoning for the decision
        
        Args:
            decision: Decision type
            hybrid_similarity: Hybrid similarity score
            semantic_similarity: Semantic similarity score
            llm_similarity: LLM-based similarity score
            analysis: Analysis results
            
        Returns:
            Reasoning text
        """
        system_prompt = self.prompts["decision_explanation"]["system"]
        user_prompt = self.prompts["decision_explanation"]["user"].format(
            decision=decision.value,
            similarity_score=f"{hybrid_similarity:.2%} (Semantic: {semantic_similarity:.2%}, LLM: {llm_similarity:.2%})",
            business_rule_match=analysis.get("business_rule_match", False),
            behavior_match=analysis.get("behavior_match", False),
            coverage_expansion=", ".join(analysis.get("coverage_expansion", []))
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=150  # Reduced tokens for faster response
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else f"Decision: {decision.value}"
            
        except Exception as e:
            # Fallback reasoning with hybrid details
            return f"Decision: {decision.value} (Hybrid: {hybrid_similarity:.2%}, Semantic: {semantic_similarity:.2%}, LLM: {llm_similarity:.2%})"
    
    def _calculate_confidence(
        self, 
        hybrid_similarity: float,
        semantic_similarity: float,
        llm_similarity: float,
        analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score using hybrid metrics
        
        Higher confidence when:
        - Semantic and LLM scores agree
        - High hybrid similarity
        - Strong business rule and behavior matches
        
        Args:
            hybrid_similarity: Hybrid similarity score
            semantic_similarity: Semantic similarity score
            llm_similarity: LLM-based similarity score
            analysis: Analysis results
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from hybrid score
        confidence = hybrid_similarity
        
        # Boost confidence when semantic and LLM scores are in agreement
        # Calculate agreement score (how close the two scores are)
        score_difference = abs(semantic_similarity - llm_similarity)
        agreement_bonus = (1.0 - score_difference) * 0.1  # Max 0.1 boost
        confidence += agreement_bonus
        
        # Additional boosts for strong matches
        if analysis.get("business_rule_match"):
            confidence += 0.05
        if analysis.get("behavior_match"):
            confidence += 0.05
        
        # Cap at 1.0
        return min(confidence, 1.0)
