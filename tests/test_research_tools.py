#!/usr/bin/env python3
"""Test script for research tools with mocked inputs and outputs"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the research_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research_agent'))

def test_internet_research():
    """Test internet_research function with mocked Exa API"""
    print("🔍 Testing internet_research...")
    
    # Mock research response
    mock_research_response = """
## Key Findings and Insights

• Sleep quality has a direct correlation with next-day productivity and cognitive performance
• Optimal sleep duration varies by individual but typically ranges from 7-9 hours for adults
• Sleep consistency (same bedtime/wake time) is often more important than total sleep duration
• Temperature, light exposure, and pre-sleep activities significantly impact sleep quality

## Relevant Statistics and Trends

• 35% of adults report getting less than 7 hours of sleep per night
• Poor sleep costs the US economy $411 billion annually in lost productivity
• Sleep tracking apps have grown 300% in usage over the past 5 years
• 68% of people who track sleep report improved sleep habits

## Expert Opinions and Studies

• Harvard Medical School: "Sleep is as important as diet and exercise for overall health"
• National Sleep Foundation: Recommends consistent sleep schedule over variable long sleep
• Recent Stanford study shows sleep quality predicts mood better than sleep quantity

## Actionable Recommendations

• Maintain consistent sleep/wake times within 30 minutes daily
• Create a dark, cool (65-68°F) sleep environment
• Limit screen time 1 hour before bed
• Track sleep patterns to identify personal optimization opportunities
    """
    
    # Mock the OpenAI client response
    mock_completion = Mock()
    mock_completion.choices = [Mock()]
    mock_completion.choices[0].message.content = mock_research_response
    
    with patch('research_agent.tools.research.researcher') as mock_researcher:
        mock_researcher.search.return_value = mock_research_response
        
        from research_agent.tools.research import internet_research
        
        # Test basic research
        query = "sleep quality and productivity correlation"
        result = internet_research(query)
        
        print("✅ Internet research result:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
        # Test research with context
        context = "Personal data shows average 6.5 hours sleep with 3.2/5 quality rating"
        result = internet_research(query, context)
        
        print("✅ Internet research with context:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print()

def test_research_correlations():
    """Test research_correlations function"""
    print("🔍 Testing research_correlations...")
    
    mock_correlation_response = """
## Internet Research: Research studies and findings about exercise and mood correlation. What do experts and scientific studies say about these correlations?

**Context from database analysis**: Personal data shows: Higher intensity workouts (>150 heart rate) correlate with improved mood ratings the following day

**Research Findings**:

## Key Findings and Insights

• Exercise releases endorphins, serotonin, and dopamine - natural mood elevators
• High-intensity exercise shows stronger acute mood benefits than low-intensity
• Exercise benefits for mood typically appear within 2-24 hours post-workout
• Consistency of exercise routine is more predictive of long-term mood benefits than intensity

## Relevant Statistics and Trends

• 30 minutes of moderate exercise can improve mood for up to 12 hours
• High-intensity interval training (HIIT) shows 23% greater mood improvement than steady-state cardio
• 89% of people report feeling "significantly better" after exercise sessions
• Exercise is as effective as antidepressants for mild to moderate depression

## Expert Opinions and Studies

• American Psychological Association: "Exercise is medicine for mental health"
• Harvard T.H. Chan School: High-intensity exercise optimizes brain-derived neurotrophic factor (BDNF)
• Journal of Clinical Psychiatry: Exercise interventions show 70% success rate for mood improvement

## Actionable Recommendations

• Aim for heart rate >75% max (roughly 150+ for most adults) for optimal mood benefits
• Schedule workouts during times when mood boost is most needed
• Track mood 2-24 hours post-workout to identify personal patterns
• Combine cardio with strength training for comprehensive mood benefits
    """
    
    with patch('research_agent.tools.research.internet_research') as mock_internet_research:
        mock_internet_research.return_value = mock_correlation_response
        
        from research_agent.tools.research import research_correlations
        
        topic = "exercise and mood correlation"
        data_insights = "Higher intensity workouts (>150 heart rate) correlate with improved mood ratings the following day"
        
        result = research_correlations(topic, data_insights)
        
        print("✅ Research correlations result:")
        print(result[:600] + "..." if len(result) > 600 else result)
        print()

def test_research_error_handling():
    """Test error handling scenarios for research tools"""
    print("🔍 Testing research error handling...")
    
    with patch('research_agent.tools.research.researcher') as mock_researcher:
        # Mock API error
        mock_researcher.search.side_effect = Exception("API key invalid")
        
        from research_agent.tools.research import internet_research, research_correlations
        
        # Test internet_research error
        result = internet_research("test query")
        print("✅ Internet research error handling:")
        print(result)
        print()
        
        # Test empty query
        result = internet_research("")
        print("✅ Empty query handling:")
        print(result)
        print()
        
        # Test research_correlations error
        result = research_correlations("test topic", "test insights")
        print("✅ Research correlations error handling:")
        print(result)
        print()

def test_exa_researcher_initialization():
    """Test ExaResearcher initialization and configuration"""
    print("🔍 Testing ExaResearcher initialization...")
    
    # Test with missing API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            from research_agent.tools.research import ExaResearcher
            researcher = ExaResearcher()
            print("❌ Should have raised EnvironmentError")
        except EnvironmentError as e:
            print("✅ Proper error handling for missing API key:")
            print(str(e))
            print()
    
    # Test with valid API key
    with patch.dict(os.environ, {'EXA_API_KEY': 'test-key-123'}):
        with patch('research_agent.tools.research.OpenAI') as mock_openai:
            from research_agent.tools.research import ExaResearcher
            
            researcher = ExaResearcher()
            print("✅ ExaResearcher initialized successfully with API key")
            
            # Verify OpenAI client was configured correctly
            mock_openai.assert_called_once_with(
                base_url="https://api.exa.ai",
                api_key="test-key-123"
            )
            print("✅ OpenAI client configured with correct parameters")
            print()

def main():
    """Run all research tool tests"""
    print("🧪 Testing Research Tools") 
    print("=" * 50)
    
    test_exa_researcher_initialization()
    test_internet_research()
    test_research_correlations()
    test_research_error_handling()
    
    print("✅ All research tool tests completed!")

if __name__ == "__main__":
    main()