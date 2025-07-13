"""
HTML report generation utilities for quantified self analysis
"""

import re


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert simple markdown to HTML for display in reports
    
    Args:
        markdown_text: Markdown formatted text
        
    Returns:
        HTML formatted text
    """
    if not markdown_text:
        return ""
    
    # Convert headings
    html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic text
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Convert bullet points
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            if line.strip():
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append('<br>')
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)


def generate_html_report_content(uploaded_files: list[tuple[str, str]], charts: list[dict], analysis: dict = None) -> str:
    """
    Generate HTML content for the quantified self analysis report
    
    Args:
        uploaded_files: List of (filename, path) tuples for uploaded files
        charts: List of chart dictionaries with 'base64' and 'alt' keys
        analysis: Dictionary with 'executive_summary' and 'focus_analysis_findings' keys
        
    Returns:
        Complete HTML content as string
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantified Self Analysis Report - Recent Trends Focus</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 30px; }}
        h2 {{ color: #34495e; margin-top: 40px; margin-bottom: 20px; }}
        h3 {{ color: #2c3e50; margin-bottom: 15px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3498db; }}
        .recent-focus {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
        .chart-container {{ margin: 30px 0; text-align: center; background: #fafafa; padding: 20px; border-radius: 8px; }}
        .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendations {{ background: #e8f6f3; padding: 20px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #27ae60; }}
        .footer {{ text-align: center; color: #7f8c8d; font-size: 14px; margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; }}
        .data-files {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }}
        .executive-summary {{ background: #f0f8ff; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #4169e1; }}
        .focus-findings {{ background: #fff0e6; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff8c00; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Quantified Self Analysis Report</h1>
        <h2 style="color: #2196f3;">🎯 Recent Trends & Current Health Trajectory</h2>
        
        <div class="recent-focus">
            <h3>🚀 Recent Data Focus</h3>
            <p>This analysis emphasizes your most recent health data to identify current trends, recent changes, and immediate actionable insights while maintaining historical context for comparison.</p>
        </div>
        
        <div class="summary">
            <h2>📋 Analysis Summary</h2>
            <p><strong>Data Sources:</strong> {len(uploaded_files)} files analyzed</p>
            <p><strong>Visualizations Generated:</strong> {len(charts)} charts</p>
            <p><strong>Focus:</strong> Recent patterns vs historical trends</p>
        </div>

        <div class="data-files">
            <h3>📁 Data Files Analyzed</h3>
            <ul>
                {chr(10).join([f"<li><strong>{name}</strong></li>" for name, _ in uploaded_files])}
            </ul>
        </div>"""

    # Add executive summary and focus findings if analysis is provided
    if analysis:
        executive_summary = analysis.get("executive_summary", "")
        focus_findings = analysis.get("focus_analysis_findings", "")
        
        if executive_summary:
            html_content += f"""
        <div class="executive-summary">
            <h2>🎯 Executive Summary</h2>
            {markdown_to_html(executive_summary)}
        </div>"""
        
        if focus_findings:
            html_content += f"""
        <div class="focus-findings">
            <h2>🔍 Focus Analysis Findings</h2>
            {markdown_to_html(focus_findings)}
        </div>"""

    html_content += """

        <h2>📈 Recent-Focused Analysis & Visualizations</h2>
        <p>The following charts emphasize your most recent data patterns while providing historical context. Each visualization highlights current trends, recent changes, and actionable insights based on your latest health metrics.</p>
"""

    # Add each chart to HTML
    for i, chart in enumerate(charts):
        html_content += f"""
        <div class="chart-container">
            <h3>Chart {i+1}: Recent Trends Analysis</h3>
            <img src="data:image/png;base64,{chart['base64']}" alt="{chart['alt']}" />
        </div>
"""

    html_content += """
        <div class="recommendations">
            <h3>🎯 Recent Insights & Immediate Actions</h3>
            <p>Based on your recent data patterns and current trajectory:</p>
            <ul>
                <li><strong>Recent Performance:</strong> Monitor how your latest metrics compare to historical averages</li>
                <li><strong>Current Trends:</strong> Pay attention to the direction your health metrics are heading</li>
                <li><strong>Immediate Opportunities:</strong> Focus on areas showing recent positive or concerning changes</li>
                <li><strong>Data-Driven Decisions:</strong> Use recent insights to adjust your health routines now</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>🤖 Generated automatically by your Quantified Self Analysis System</p>
            <p>Report focused on recent data trends and current health trajectory</p>
        </div>
    </div>
</body>
</html>
"""

    return html_content


def generate_analysis_prompt(uploaded_files: list[tuple[str, str]]) -> str:
    """
    Generate the analysis prompt for the AI with recent data focus and iterative workflow
    
    Args:
        uploaded_files: List of (filename, path) tuples for uploaded files
        
    Returns:
        Analysis prompt string
    """
    return f"""
# Iterative Quantified Self Data Analysis with Recent Data Focus

I have uploaded the following quantified self CSV files to the sandbox:
{chr(10).join([f"- {name} at {path}" for name, path in uploaded_files])}

## Your Task
You have access to THREE tools for an iterative analysis process:

1. **`run_python_code`** - Execute Python code to explore, analyze, and create visualizations
2. **`search_health_insights`** - Search for health research and insights to enhance your analysis
3. **`finalize_analysis`** - Call when satisfied with your analysis to end the session and provide comprehensive markdown summary

## Iterative Workflow
Take your time to build a comprehensive analysis through multiple iterations:

### Phase 1: Data Exploration
- Load and examine each CSV file
- Understand data structure, date ranges, and patterns
- Identify the most recent entries in each dataset

### Phase 2: Analysis Development  
- Create initial visualizations focusing on RECENT DATA
- Compare recent patterns (last 7-14 days) with historical averages
- Highlight changes, improvements, or concerning trends in recent data
- Show how current behavior differs from past patterns

### Phase 3: Refinement & Enhancement
- Improve visualizations based on initial results
- Add cross-domain correlations between different health metrics
- Focus on recent correlations and emerging patterns
- Create compelling narrative around recent trends

### Phase 4: Research Enhancement
- Use `search_health_insights` throughout your analysis to validate findings
- Research any unusual patterns, correlations, or health concerns you discover
- Integrate research findings into your analysis and recommendations

### Phase 5: Finalization ⚠️ CRITICAL
- **MANDATORY**: You MUST call `finalize_analysis` within 15 iterations to complete the analysis
- **Target**: Aim for 3-5 high-quality visualizations that tell a complete story
- **Quality over Quantity**: Better to finalize with fewer excellent charts than reach max iterations
- **Comprehensive Summary**: Provide detailed markdown analysis including key findings, research insights, and specific actionable recommendations
- **Complete Story**: Ensure charts create a cohesive narrative about recent health trajectory

## Analysis Priorities (Focus on RECENT DATA)
- **Recent Performance**: How are recent workouts, nutrition, sleep compared to historical?
- **Current Trends**: What direction are the metrics heading in the last 1-2 weeks?  
- **Recent Correlations**: Are there new patterns emerging in recent data?
- **Immediate Insights**: What can be learned from the most recent entries?

## Visualization Guidelines
- Use matplotlib/seaborn with professional styling
- Highlight recent data points with different colors/markers  
- Include trend lines showing recent direction vs historical
- Add annotations for significant recent changes
- Focus on actionable insights from recent patterns
- Compare "recent" vs "historical" periods explicitly

## Technical Notes
- Available data domains may include workouts, food, sleep, mood, etc.
- Adapt your analysis to whatever data is actually present
- Use proper error handling for missing data
- Generate charts that tell a story about current health trajectory

**Key Question**: What story does the RECENT data tell about the user's current health trajectory?

Start by exploring the data structure to understand what you're working with.
"""