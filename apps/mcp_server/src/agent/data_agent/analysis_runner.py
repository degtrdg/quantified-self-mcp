"""
Analysis runner utilities for e2b sandbox integration
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from .exa_search import ExaSearcher
import weave

load_dotenv()


class AnalysisRunner:
    """Handles running analysis code in e2b sandbox"""

    def __init__(self):
        self.sandbox = Sandbox(api_key=os.getenv("E2B_API_KEY"))
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.exa_searcher = ExaSearcher()

    def upload_csv_to_sandbox(self, csv_data: str, filename: str) -> str:
        """
        Upload CSV data to sandbox

        Args:
            csv_data: CSV content as string
            filename: Name for the file in sandbox

        Returns:
            Path to uploaded file in sandbox
        """
        dataset_path = self.sandbox.files.write(filename, csv_data)
        print(f"Uploaded {filename} to sandbox at {dataset_path.path}")
        return dataset_path.path

    def upload_csv_files(
        self, loaded_files: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """
        Upload multiple CSV files to sandbox

        Args:
            loaded_files: List of (filename, csv_content) tuples

        Returns:
            List of (filename, sandbox_path) tuples
        """
        uploaded_files = []

        for filename, csv_data in loaded_files:
            try:
                path = self.upload_csv_to_sandbox(csv_data, filename)
                uploaded_files.append((filename, path))
            except Exception as e:
                print(f"Error uploading {filename}: {e}")

        return uploaded_files

    @weave.op()
    def _create_anthropic_completion(self, messages, tools):
        """Create Anthropic completion with weave tracking"""
        return self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=messages,
            tools=tools,
        )

    @weave.op()
    def generate_analysis_iteratively(self, analysis_prompt: str) -> list[dict] | None:
        """
        Generate analysis code iteratively with AI feedback loop

        Args:
            analysis_prompt: Initial prompt for AI to generate analysis code

        Returns:
            List of chart dictionaries with base64 images or None if failed
        """
        print("Starting iterative analysis generation...")

        # Start conversation with initial prompt
        messages = [{"role": "user", "content": analysis_prompt}]

        # Define available tools for the iterative process
        tools = [
            {
                "name": "run_python_code",
                "description": "Run Python code to test and iterate on analysis. Use this to explore data, create visualizations, and refine your approach.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute for analysis",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "search_health_insights",
                "description": "Search for health and fitness insights using Exa API to enhance analysis with external research and recommendations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for health insights (e.g., 'optimal protein intake for strength training', 'sleep quality improvement strategies')",
                        },
                        "context": {
                            "type": "string", 
                            "description": "Optional context about user's data to make search more relevant",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "finalize_analysis",
                "description": "Call this when you are satisfied with your analysis and visualizations to end the iterative process and generate the final report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "executive_summary": {
                            "type": "string",
                            "description": "Comprehensive markdown analysis that will serve as the executive summary at the top of the report. Include key findings, patterns discovered, research insights, recommendations, and conclusions. This should be detailed and informative, not brief.",
                        },
                        "focus_analysis_findings": {
                            "type": "string",
                            "description": "If a specific focus was provided (like 'stomach hurts after pushups'), detail your findings related to that focus, including data correlations found, research insights, and specific recommendations. If no specific focus, leave empty.",
                        },
                    },
                    "required": ["executive_summary"],
                },
            },
        ]

        iteration_count = 0
        max_iterations = 20  # Increased from 10 to allow more thorough analysis
        all_charts = []
        final_analysis = None

        while iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n{'='*80}")
            print(f"🔄 ANALYSIS ITERATION {iteration_count}")
            print(f"{'='*80}")

            # Get AI response
            print("🤖 Sending request to AI...")
            response = self._create_anthropic_completion(messages, tools)

            # Build assistant message with both text and tool calls
            assistant_message = {"role": "assistant", "content": []}

            # Add text content if present
            text_content = []
            tool_calls = []

            for content_block in response.content:
                if content_block.type == "text":
                    text_content.append(content_block.text)
                elif content_block.type == "tool_use":
                    tool_calls.append(content_block)

            # Print AI's text response
            if text_content:
                ai_text = "\n".join(text_content)
                print(f"\n💭 AI REASONING:")
                print(f"{'─'*60}")
                print(ai_text)
                print(f"{'─'*60}")
                
                assistant_message["content"].append(
                    {"type": "text", "text": ai_text}
                )

            # Process tool calls
            tool_used = False
            tool_results = []
            
            print(f"\n🛠️ TOOL CALLS: {len(tool_calls)} tool(s) to execute")

            for i, tool_call in enumerate(tool_calls, 1):
                tool_used = True
                tool_name = tool_call.name
                tool_input = tool_call.input
                tool_id = getattr(tool_call, "id", f"tool_{iteration_count}_{i}")

                print(f"\n🔧 Tool {i}/{len(tool_calls)}: {tool_name}")
                print(f"   ID: {tool_id}")

                # Add tool call to assistant message
                assistant_message["content"].append(
                    {
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tool_name,
                        "input": tool_input,
                    }
                )

                if tool_name == "run_python_code":
                    code = tool_input.get("code")
                    if code:
                        # Show the code being executed
                        print(f"\n🐍 EXECUTING PYTHON CODE:")
                        print(f"{'─'*40}")
                        # Show first few lines of code for context
                        code_lines = code.split('\n')
                        preview_lines = min(10, len(code_lines))
                        for line_num, line in enumerate(code_lines[:preview_lines], 1):
                            print(f"{line_num:2d}: {line}")
                        if len(code_lines) > preview_lines:
                            print(f"... ({len(code_lines) - preview_lines} more lines)")
                        print(f"{'─'*40}")
                        
                        execution_result = self.execute_code_iteration(code)

                        # Print execution results
                        print(f"\n📊 EXECUTION RESULT:")
                        if execution_result["success"]:
                            print(f"✅ Success!")
                            if execution_result.get("charts"):
                                chart_count = len(execution_result["charts"])
                                print(f"📈 Generated {chart_count} chart(s)")
                                all_charts.extend(execution_result["charts"])
                            
                            # Show stdout output if available - this was missing before!
                            if execution_result.get("stdout"):
                                print(f"\n💬 STDOUT OUTPUT:")
                                print(f"{'─'*40}")
                                print(execution_result["stdout"])
                                print(f"{'─'*40}")
                            else:
                                print(f"\n⚠️ No stdout output captured")
                            
                            print(f"Summary: {execution_result['message']}")
                        else:
                            print(f"❌ Failed: {execution_result['message']}")

                        # Store tool result with comprehensive feedback
                        result_content = execution_result["message"]
                        if execution_result.get("stdout"):
                            result_content += f"\n\nCode Output:\n{execution_result['stdout']}"
                        
                        tool_results.append(
                            {
                                "tool_call_id": tool_id,
                                "type": "tool_result",
                                "content": result_content,
                            }
                        )

                elif tool_name == "search_health_insights":
                    query = tool_input.get("query")
                    context = tool_input.get("context", "")
                    
                    if query:
                        print(f"\n🔍 SEARCHING HEALTH INSIGHTS")
                        print(f"Query: {query}")
                        if context:
                            print(f"Context: {context[:100]}...")
                        
                        search_result = self.exa_searcher.search_health_insights(query, context)
                        print(f"✅ Search completed")
                        
                        # Log search results for debugging
                        print(f"\n📋 SEARCH RESULTS PREVIEW:")
                        print(f"{'─'*40}")
                        print(search_result[:500] + "..." if len(search_result) > 500 else search_result)
                        print(f"{'─'*40}")
                        print(f"📏 Full search result length: {len(search_result)} characters")
                        
                        tool_results.append(
                            {
                                "tool_call_id": tool_id,
                                "type": "tool_result",
                                "content": f"Health Insights Search Results:\n\n{search_result}",
                            }
                        )
                    else:
                        tool_results.append(
                            {
                                "tool_call_id": tool_id,
                                "type": "tool_result",
                                "content": "Error: Query parameter is required for health insights search",
                            }
                        )

                elif tool_name == "finalize_analysis":
                    executive_summary = tool_input.get("executive_summary", "Analysis completed")
                    focus_findings = tool_input.get("focus_analysis_findings", "")
                    
                    print(f"\n🏁 FINALIZING ANALYSIS")
                    print(f"Executive Summary: {executive_summary[:100]}...")
                    if focus_findings:
                        print(f"Focus Findings: {focus_findings[:100]}...")
                    print(f"📊 Total charts generated: {len(all_charts)}")
                    
                    # Store final analysis
                    final_analysis = {
                        "executive_summary": executive_summary,
                        "focus_analysis_findings": focus_findings
                    }
                    
                    # Return both charts and analysis
                    return {
                        "charts": all_charts if all_charts else [],
                        "analysis": final_analysis
                    }

            # Add assistant message if it has content
            if assistant_message["content"]:
                messages.append(assistant_message)

            # Add tool results as user message with proper format
            if tool_results:
                user_message = {"role": "user", "content": []}
                for tool_result in tool_results:
                    user_message["content"].append({
                        "type": "tool_result",
                        "tool_use_id": tool_result["tool_call_id"],
                        "content": tool_result["content"]
                    })
                messages.append(user_message)

            # Print iteration summary
            print(f"\n📝 ITERATION {iteration_count} SUMMARY:")
            print(f"   🛠️ Tools executed: {len(tool_calls)}")
            print(f"   📊 Charts generated this iteration: {len([r for r in tool_results if 'Generated' in r.get('content', '')])}")
            print(f"   📈 Total charts so far: {len(all_charts)}")

            # If no tools were used, break the loop
            if not tool_used:
                print("⚠️ No tools used, ending iteration")
                break

        print(f"\n⚠️ Reached maximum iterations ({max_iterations})")
        print(f"📊 Final chart count: {len(all_charts)}")
        
        # If we reach max iterations without finalize_analysis being called
        if all_charts:
            return {
                "charts": all_charts,
                "analysis": {
                    "executive_summary": "Analysis completed but reached maximum iterations without finalization. Charts were generated successfully.",
                    "focus_analysis_findings": ""
                }
            }
        else:
            return None

    def execute_code_iteration(self, code: str) -> dict:
        """
        Execute code for one iteration and return results

        Args:
            code: Python code to execute

        Returns:
            Dictionary with execution results and any charts
        """
        try:
            execution = self.sandbox.run_code(code)

            if execution.error:
                return {
                    "success": False,
                    "message": f"Error: {execution.error.name} - {execution.error.value}",
                    "charts": [],
                }

            # Collect any new charts from this execution
            charts = []
            for i, result in enumerate(execution.results):
                if result.png:
                    charts.append(
                        {
                            "title": f"Chart {len(charts) + 1}",
                            "base64": result.png,
                            "alt": f"Analysis chart {len(charts) + 1}",
                        }
                    )

            # Format execution output - get stdout from logs
            output_text = ""
            
            # Get stdout from execution.logs.stdout
            if hasattr(execution, 'logs') and hasattr(execution.logs, 'stdout'):
                if execution.logs.stdout:
                    # stdout is a list, join all entries
                    output_text = "\n".join(execution.logs.stdout)
            
            # Also check execution.results for any text output
            for result in execution.results:
                if hasattr(result, 'text') and result.text:
                    output_text += "\n" + result.text

            success_msg = "Code executed successfully"
            if charts:
                success_msg += f" - Generated {len(charts)} chart(s)"

            return {
                "success": True, 
                "message": success_msg, 
                "charts": charts,
                "stdout": output_text.strip() if output_text.strip() else None
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Execution error: {str(e)}",
                "charts": [],
            }

    def run_analysis_code(self, analysis_code: str) -> list[dict] | None:
        """
        Run analysis code in sandbox and extract charts

        Args:
            analysis_code: Python code to execute

        Returns:
            List of chart dictionaries with base64 images or None if failed
        """
        print("Running recent-focused analysis in sandbox...")
        execution = self.sandbox.run_code(analysis_code)
        print("Analysis completed!")

        if execution.error:
            print("Analysis code had an error:")
            print(execution.error.name)
            print(execution.error.value)
            print(execution.error.traceback)
            return None

        # Collect all charts as base64 images
        charts = []
        for i, result in enumerate(execution.results):
            if result.png:
                charts.append(
                    {
                        "title": f"Analysis Chart {i + 1}",
                        "base64": result.png,
                        "alt": f"Recent-focused quantified self analysis chart {i + 1}",
                    }
                )

        return charts if charts else None

    def save_html_report(
        self, html_content: str, filename: str = "quantified_self_report.html"
    ) -> str:
        """
        Save HTML report to sandbox for download

        Args:
            html_content: HTML content to save
            filename: Filename for the HTML report

        Returns:
            Success message with download instructions
        """
        self.sandbox.files.write(filename, html_content)
        print(f"✅ HTML report saved as '{filename}' in sandbox")
        print(f"📁 Download using: sbx.files.read('{filename}')")

        return f"Recent-focused HTML report generated successfully! File saved as '{filename}' in sandbox. Use sbx.files.read('{filename}') to download."
