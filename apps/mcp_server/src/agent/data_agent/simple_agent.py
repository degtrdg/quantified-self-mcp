"""Simple Data Analysis Agent using standalone database helpers

This agent processes queries using Claude and direct database access without MCP framework.
"""

import asyncio
import csv
import os
from typing import Any, Dict, List

from anthropic import Anthropic
from database_helpers import db_helper, execute_tool, get_database_tools, query_data


class SimpleDataAgent:
    """Simple agent for data analysis using direct database access"""

    def __init__(self):
        self.anthropic = Anthropic()
        self.tools = get_database_tools()

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [{"role": "user", "content": query}]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=self.tools,
        )

        # Process response and handle tool calls
        final_text = []

        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                if tool_name == "final_query":
                    result = self._handle_final_query(tool_args["query"])
                else:
                    result = execute_tool(tool_name, **tool_args)

                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                final_text.append(result)

                # Continue conversation with tool results
                messages.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": content.text
                                if hasattr(content, "text")
                                else "",
                            },
                            {
                                "type": "tool_use",
                                "id": content.id,
                                "name": tool_name,
                                "input": tool_args,
                            },
                        ],
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result,
                            }
                        ],
                    }
                )

                # Get next response from Claude
                follow_up = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                for follow_content in follow_up.content:
                    if follow_content.type == "text":
                        final_text.append(follow_content.text)

        return "\\n".join(final_text)

    def _handle_final_query(self, sql_query: str) -> str:
        """Handle final query and export to CSV"""
        try:
            # Execute the query
            results = db_helper.execute_query(sql_query)

            if not results:
                return "❌ No data returned from query"

            # Create CSV file
            csv_filename = "data_export.csv"
            csv_path = os.path.join("data", csv_filename)

            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)

            # Write to CSV
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                if results:
                    fieldnames = results[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)

            return f"✅ **Query executed successfully!**\\n\\n**SQL**: `{sql_query}`\\n**Rows exported**: {len(results)}\\n**File**: `{csv_path}`\\n\\n🎯 **Ready for analysis agent** - CSV file created for matplotlib visualizations"

        except Exception as e:
            return f"❌ Error executing final query: {str(e)}"

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\\n🤖 Simple Data Analysis Agent Started!")
        print("📊 Connected to quantified self database")
        print("💡 Ask questions about your data or request analyses")
        print("Type 'quit' to exit.\\n")

        while True:
            try:
                query = input("Query: ").strip()

                if query.lower() == "quit":
                    break

                print("\\n🔄 Processing...")
                response = await self.process_query(query)
                print("\\n" + response)
                print("\\n" + "=" * 50)

            except Exception as e:
                print(f"\\n❌ Error: {str(e)}")

    def close(self):
        """Close database connection"""
        db_helper.close()


# Example usage functions for standalone use
def run_simple_query(sql: str) -> str:
    """Run a simple SQL query and return formatted results"""
    return query_data(sql)


def export_query_to_csv(sql: str, filename: str = "export.csv") -> str:
    """Execute query and export results to CSV"""
    try:
        results = db_helper.execute_query(sql)

        if not results:
            return "❌ No data returned from query"

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        csv_path = os.path.join("data", filename)

        # Write to CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        return f"✅ Exported {len(results)} rows to {csv_path}"

    except Exception as e:
        return f"❌ Export error: {str(e)}"


async def main():
    """Main entry point"""
    agent = SimpleDataAgent()
    try:
        await agent.chat_loop()
    finally:
        agent.close()


if __name__ == "__main__":
    asyncio.run(main())
