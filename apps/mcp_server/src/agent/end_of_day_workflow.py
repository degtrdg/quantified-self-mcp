"""
End of day analysis workflow for quantified self data
"""

import json
from typing import Any, Dict, Optional

import requests

from .data_agent.analysis_runner import AnalysisRunner
from .data_agent.data_discovery import (
    discover_csv_files,
    get_default_data_path,
    load_csv_files,
)
from .data_agent.html_generator import (
    generate_analysis_prompt,
    generate_html_report_content,
)


class EndOfDayAnalyzer:
    """Handles end-of-day analysis and email delivery via n8n"""

    def __init__(self, n8n_webhook_url: Optional[str] = None):
        self.n8n_webhook_url = n8n_webhook_url
        self.runner = AnalysisRunner()

    def generate_analysis_report(self, focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report for end-of-day summary

        Args:
            focus: Optional focus area for the analysis (e.g., "workout performance", "sleep quality")

        Returns:
            Dictionary containing analysis results, charts, and insights
        """
        # Discover and load CSV files
        data_export_path = get_default_data_path()
        csv_files = discover_csv_files(data_export_path)

        if not csv_files:
            return {
                "success": False,
                "error": "No CSV data files found for analysis",
                "charts": [],
                "insights": "No data available for analysis",
            }

        loaded_files = load_csv_files(data_export_path, csv_files)

        if not loaded_files:
            return {
                "success": False,
                "error": "Failed to load CSV files",
                "charts": [],
                "insights": "Data loading failed",
            }

        # Upload files to sandbox
        uploaded_files = self.runner.upload_csv_files(loaded_files)

        if not uploaded_files:
            return {
                "success": False,
                "error": "Failed to upload files to analysis sandbox",
                "charts": [],
                "insights": "File upload failed",
            }

        # Generate enhanced analysis prompt for end-of-day summary
        analysis_prompt = self._create_end_of_day_prompt(uploaded_files, focus)

        # Generate analysis iteratively with AI
        analysis_result = self.runner.generate_analysis_iteratively(analysis_prompt)

        if not analysis_result:
            return {
                "success": False,
                "error": "Analysis failed to generate insights",
                "charts": [],
                "insights": "Analysis generation failed",
                "analysis": None,
            }

        charts = analysis_result.get("charts", [])
        analysis_text = analysis_result.get("analysis", {})

        return {
            "success": True,
            "charts": charts,
            "analysis": analysis_text,
            "insights": "End-of-day analysis completed successfully",
            "file_count": len(uploaded_files),
            "chart_count": len(charts),
            "uploaded_files": uploaded_files,
        }

    def _create_end_of_day_prompt(
        self, uploaded_files: list, focus: Optional[str] = None
    ) -> str:
        """Create specialized prompt for end-of-day analysis"""
        base_prompt = generate_analysis_prompt(uploaded_files)

        # Add focus-specific instructions if provided
        focus_section = ""
        if focus:
            focus_section = f"""

🎯 DETAILED ANALYSIS FOCUS: 
"{focus}"

CRITICAL INSTRUCTIONS FOR THIS FOCUS:
1. **Primary Investigation**: Treat this as your main research question/hypothesis to explore
2. **Correlation Analysis**: Actively look for patterns and correlations related to the symptoms, observations, or concerns mentioned
3. **Time-based Patterns**: Examine timing relationships (e.g., "headaches on workout days", "tired after workouts")
4. **Multi-metric Relationships**: If multiple health areas are mentioned, create comprehensive cross-domain analysis
5. **Symptom Tracking**: If symptoms are described, correlate them with all relevant tracked metrics
6. **Hypothesis Testing**: Form and test specific hypotheses based on the user's observations
7. **Targeted Recommendations**: Provide specific, actionable insights addressing the focus area
8. **Data Discovery**: Look for hidden patterns that might explain the user's concerns or observations

While maintaining comprehensive coverage, make this focus area the central theme of your entire analysis.

"""

        end_of_day_enhancement = f"""{focus_section}

SPECIAL FOCUS FOR END-OF-DAY ANALYSIS:
1. **Today's Summary**: Focus heavily on today's activities and how they compare to recent patterns
2. **Health Score**: Calculate an overall daily health score based on all tracked metrics
3. **Key Achievements**: Identify what went well today and celebrate progress
4. **Areas for Improvement**: Spot opportunities for tomorrow and upcoming days
5. **Trend Analysis**: How does today fit into weekly/monthly patterns?
6. **Research Integration**: Use the search_health_insights tool to provide evidence-based recommendations

VISUALIZATION PRIORITIES:
- Today's metrics vs recent averages
- Weekly trend charts showing progress
- Health score breakdown by category
- Correlation insights between different health metrics

RESEARCH ENHANCEMENT:
Use the search_health_insights tool throughout your analysis to:
- Validate observed patterns against research
- Get recommendations for improvement areas
- Provide context for unusual metrics or achievements
- Suggest evidence-based next steps

TONE: Encouraging, insightful, and actionable - this is a daily review to motivate continued progress.
"""

        return base_prompt + end_of_day_enhancement

    def send_to_n8n_workflow(
        self, analysis_data: Dict[str, Any], uploaded_files: list = None
    ) -> Dict[str, Any]:
        """
        Send analysis results to n8n workflow for email delivery

        Args:
            analysis_data: Analysis results including charts and insights
            uploaded_files: List of (filename, path) tuples for uploaded files

        Returns:
            Response from n8n webhook
        """
        if not self.n8n_webhook_url:
            return {"success": False, "error": "No n8n webhook URL configured"}

        # Generate HTML report
        charts = analysis_data.get("charts", [])
        analysis_text = analysis_data.get("analysis", {})

        html_content = ""
        if uploaded_files:
            html_content = generate_html_report_content(
                uploaded_files, charts, analysis_text
            )
        
        # Ensure html_content is a string and not None/undefined
        if not html_content:
            html_content = "Your daily health analysis is ready."
        
        # Save HTML to file
        try:
            import os
            from datetime import datetime
            
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{reports_dir}/daily_health_report_{timestamp}.html"
            
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 HTML report saved to: {html_filename}")
            
        except Exception as e:
            print(f"⚠️ Failed to save HTML report: {e}")

        # Prepare payload for n8n - ensure email is always a string
        payload = {
            "email": str(html_content).strip()
        }

        print(f"🔍 Sending payload to n8n:")
        print(f"   - URL: {self.n8n_webhook_url}")
        print(f"   - Payload keys: {list(payload.keys())}")
        print(f"   - Email content length: {len(html_content) if html_content else 0}")
        print(f"   - Charts count: {len(charts)}")

        try:
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,  # Increase timeout to 2 minutes for email processing
            )

            print(f"🔍 n8n Response:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response text: {response.text}")

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Analysis sent to email workflow successfully",
                    "response": response.json() if response.content else {},
                }
            else:
                return {
                    "success": False,
                    "error": f"n8n webhook failed with status {response.status_code}: {response.text}",
                }

        except requests.exceptions.Timeout:
            print(f"⚠️ n8n webhook timeout (120s) - email workflow may still be processing")
            return {
                "success": True,  # Consider it successful since webhook received the data
                "message": "Email workflow started (timeout occurred but processing continues)",
                "warning": "Webhook timed out after 120s but n8n workflow is likely still processing the email"
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ n8n webhook error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to send to n8n workflow: {str(e)}",
            }

    def run_end_of_day_analysis(self, focus: Optional[str] = None) -> str:
        """
        Complete end-of-day workflow: analyze data and send email

        Args:
            focus: Optional focus area for the analysis

        Returns:
            Summary of the analysis and delivery process
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Generate analysis
        focus_msg = f" with focus on '{focus}'" if focus else ""
        logger.info(f"🔄 Generating end-of-day analysis{focus_msg}...")
        print(f"🔄 Generating end-of-day analysis{focus_msg}...")
        
        logger.info("📊 Starting analysis report generation...")
        analysis_result = self.generate_analysis_report(focus)

        if not analysis_result["success"]:
            error_msg = f"❌ Analysis failed: {analysis_result['error']}"
            logger.error(error_msg)
            return error_msg

        logger.info(f"✅ Analysis generation completed with {analysis_result['chart_count']} charts")
        print(f"✅ Analysis completed with {analysis_result['chart_count']} charts")

        # Send to n8n if webhook URL is configured
        if self.n8n_webhook_url:
            logger.info("📧 Sending to email workflow...")
            print("📧 Sending to email workflow...")
            uploaded_files = analysis_result.get("uploaded_files", [])
            
            logger.info(f"📎 Uploading {len(uploaded_files)} files to n8n workflow")
            email_result = self.send_to_n8n_workflow(analysis_result, uploaded_files)

            if email_result["success"]:
                success_msg = f"✅ End-of-day analysis complete! Generated {analysis_result['chart_count']} charts and sent email summary via n8n workflow."
                logger.info(success_msg)
                return success_msg
            else:
                warning_msg = f"⚠️ Analysis completed ({analysis_result['chart_count']} charts) but email delivery failed: {email_result['error']}"
                logger.warning(warning_msg)
                return warning_msg
        else:
            no_email_msg = f"✅ End-of-day analysis complete! Generated {analysis_result['chart_count']} charts. Email delivery not configured."
            logger.info(no_email_msg)
            return no_email_msg

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime

        return datetime.now().isoformat()

    def _get_today_date(self) -> str:
        """Get today's date in readable format"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")
