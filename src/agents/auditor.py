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


    # Internal helpers
    def _collect_python_files(self, root: Path) -> List[Path]:
        return [path for path in root.rglob("*.py") if path.is_file()]

    def _run_static_analysis(self, files: List[Path]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Runs pylint in JSON mode for each file.
        """
        results: Dict[str, List[Dict[str, Any]]] = {}

        for file_path in files:
            try:
                completed = subprocess.run(
                    [
                        "pylint",
                        str(file_path),
                        "--output-format=json",
                        "--score=n"
                    ],
                    capture_output=True,
                    text=True,
                    check=False
                )

                pylint_output = json.loads(completed.stdout) if completed.stdout.strip() else []

                issues = []
                for item in pylint_output:
                    issues.append({
                        "line": item.get("line"),
                        "symbol": item.get("symbol"),
                        "message": item.get("message"),
                        "category": item.get("type")
                    })

                results[str(file_path)] = issues

            except Exception as e:
                results[str(file_path)] = [{
                    "line": None,
                    "symbol": "auditor_error",
                    "message": str(e),
                    "category": "fatal"
                }]

        return results

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
        )

        report_section = "Static analysis findings:\n"
        for file_path, issues in static_report.items():
            report_section += f"\nFile: {file_path}\n"
            if not issues:
                report_section += "  No issues detected.\n"
            else:
                for issue in issues:
                    report_section += (
                        f"  - Line {issue['line']}: [{issue['category']}] {issue['message']}\n"
                    )

        closing = (
            "\nReturn your analysis in clear natural language.\n"
            "Do NOT use JSON. Do NOT invent new files.\n"
        )

        return intro + instructions + report_section + closing
        # building the plan 

    def _build_refactoring_plan(
        self,
        static_report: Dict[str, List[Dict[str, Any]]],
        llm_summaries: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Converts tool + LLM reasoning into a structured plan.
        """
        files_plan = []

        for file_path, issues in static_report.items():
            files_plan.append({
                "file_path": file_path,
                "issue_count": len(issues),
                "static_issues": issues,
                "llm_analysis_summary": llm_summaries.get(file_path, "")
            })

        return {
            "auditor_version": self.version,
            "generated_at": datetime.utcnow().isoformat(),
            "files_overview": files_plan
        }
