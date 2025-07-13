#!/usr/bin/env python3
"""
FastAPI server for end-of-day analysis
Handles long-running analysis tasks without MCP timeouts
"""

import logging
import os
import threading
from datetime import datetime
from typing import Optional

import uvicorn
import weave
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Add the project structure to Python path
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the analyzer
from apps.mcp_server.src.agent.end_of_day_workflow import EndOfDayAnalyzer

# Initialize Weave for tracking
weave.init("end-of-day-analysis")

app = FastAPI(title="End of Day Analysis Server", version="1.0.0")

# Store for tracking analysis status
analysis_status = {}


class AnalysisRequest(BaseModel):
    focus: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str
    message: str
    log_file: str
    analysis_id: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze", response_model=AnalysisResponse)
@weave.op()
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start end-of-day analysis in background"""

    # Create analysis ID and log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_id = f"analysis_{timestamp}"
    log_file = f"/tmp/end_of_day_analysis_{timestamp}.log"

    # Configure logging for this analysis
    logger = logging.getLogger(analysis_id)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Add file and console handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Initialize status tracking
    analysis_status[analysis_id] = {
        "status": "started",
        "start_time": datetime.now().isoformat(),
        "log_file": log_file,
        "focus": request.focus,
    }

    # Add background task
    background_tasks.add_task(
        run_analysis_background, analysis_id, request.focus, logger
    )

    focus_msg = f" (focus: {request.focus})" if request.focus else ""
    return AnalysisResponse(
        status="started",
        message=f"End-of-day analysis started{focus_msg}!",
        log_file=log_file,
        analysis_id=analysis_id,
    )


@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of a specific analysis"""
    if analysis_id not in analysis_status:
        return {"error": "Analysis not found"}

    return analysis_status[analysis_id]


@app.get("/logs/{analysis_id}")
async def get_analysis_logs(analysis_id: str):
    """Get logs for a specific analysis"""
    if analysis_id not in analysis_status:
        return {"error": "Analysis not found"}

    log_file = analysis_status[analysis_id]["log_file"]

    try:
        with open(log_file, "r") as f:
            logs = f.read()
        return {"logs": logs}
    except FileNotFoundError:
        return {"error": "Log file not found"}


@weave.op()
async def run_analysis_background(
    analysis_id: str, focus: Optional[str], logger: logging.Logger
):
    """Run the analysis in background"""
    try:
        focus_msg = f" with focus on '{focus}'" if focus else ""
        logger.info(f"🔄 Starting end-of-day analysis{focus_msg}")

        # Update status
        analysis_status[analysis_id]["status"] = "running"
        analysis_status[analysis_id]["stage"] = "initializing"

        # Get webhook URL from environment variable (try both possible names)
        webhook_url = os.getenv("N8N_WEBHOOK_URL") or os.getenv("N8N_EMAIL_WEBHOOK_URL")
        logger.info(f"📧 N8N webhook configured: {'Yes' if webhook_url else 'No'}")

        # Initialize analyzer
        logger.info("🚀 Initializing EndOfDayAnalyzer...")
        analysis_status[analysis_id]["stage"] = "analyzing"
        analyzer = EndOfDayAnalyzer(n8n_webhook_url=webhook_url)

        # Run complete workflow with optional focus
        logger.info("🔄 Running analysis workflow...")
        result = analyzer.run_end_of_day_analysis(focus=focus)

        logger.info(f"✅ Analysis completed successfully: {result}")

        # Update final status
        analysis_status[analysis_id]["status"] = "completed"
        analysis_status[analysis_id]["stage"] = "finished"
        analysis_status[analysis_id]["result"] = result
        analysis_status[analysis_id]["end_time"] = datetime.now().isoformat()

        # Write final result to log file
        with open(analysis_status[analysis_id]["log_file"], "a") as f:
            f.write(f"\n\n=== FINAL RESULT ===\n{result}\n")

    except Exception as e:
        logger.error(f"❌ Analysis failed with error: {str(e)}", exc_info=True)

        # Update error status
        analysis_status[analysis_id]["status"] = "failed"
        analysis_status[analysis_id]["error"] = str(e)
        analysis_status[analysis_id]["end_time"] = datetime.now().isoformat()


if __name__ == "__main__":
    print("🚀 Starting End-of-Day Analysis Server...")
    print("📊 Server will be available at http://localhost:8001")
    print("📖 API docs at http://localhost:8001/docs")
    print("🔍 Health check at http://localhost:8001/health")

    uvicorn.run(app, host="0.0.0.0", port=8001)
