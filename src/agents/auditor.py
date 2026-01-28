import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Any, List

from src.utils.logger import log_experiment, ActionType


class Auditor:
    """
    Auditor Agent:
    - Reads Python source files
    - Runs static analysis (pylint)
    - Uses an LLM to reason about refactoring strategy
    - Produces a structured refactoring plan
    """

    def __init__(self, agent_name: str = "Auditor_Agent"):
        self.agent_name = agent_name
        self.version = "1.0"

    # the Public entry point
    def run(self, target_dir: str, llm_callable: Callable[[str], str]) -> Dict[str, Any]:
        target_path = Path(target_dir)

        if not target_path.exists() or not target_path.is_dir():
            raise ValueError(f"Invalid target directory: {target_dir}")

        python_files = self._collect_python_files(target_path)
        static_report = self._run_static_analysis(python_files)

        # Generate and log LLM analysis per file
        file_llm_summaries = {}
        for file_path in python_files:
            file_issues = static_report[str(file_path)]
            file_prompt = self._build_prompt({str(file_path): file_issues})
            file_response = llm_callable(file_prompt)
            file_llm_summaries[str(file_path)] = file_response
              # the Log per file
            log_experiment(
                agent_name=self.agent_name,
                model_used="google-ai (via orchestrator)",
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": str(file_path),
                    "input_prompt": file_prompt,
                    "output_response": file_response,
                    "issues_found": len(file_issues)
                },
                status="SUCCESS"
            )

        # Build structured plan for all files
        plan = self._build_refactoring_plan(static_report, file_llm_summaries)

        return plan
)

   def _build_prompt(self, static_report: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Builds a unique prompt for LLM reasoning.
        """
        # the analysing prompt and instructions
        intro = (
            "You are a senior Python software auditor participating in a scientific "
            "software maintenance experiment.\n\n"
            "Your task is to analyze static analysis results and propose a refactoring strategy.\n"
            "You MUST NOT rewrite code. You only reason and plan.\n\n"
        )

        instructions = (
            "For each file:\n"
            "- Summarize the main quality problems\n"
            "- Identify risk level (LOW / MEDIUM / HIGH)\n"
            "- Propose ordered refactoring steps\n"
            "- Avoid implementation details\n\n"
        ))