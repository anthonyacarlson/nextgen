"""
Tessl Scanning Tool

Runs tessl security scans on skills found in the repository and returns
a scored report of findings.
"""

import subprocess
import os
import shutil
from typing import Optional, Type
#from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class TesslScanInput(BaseModel):
    """Input schema for the Tessl scanning tool"""

    path: str = Field(
        description="Path to the skill file or directory to scan with tessl. "
        "Can be a single SKILL.md file or a directory containing multiple skills."
    )


class TesslScanTool(BaseTool):
    """
    Runs tessl security scans on skill files or directories and returns
    a scored report of findings including vulnerabilities, misconfigurations,
    and best practice violations.
    """

    name: str = "tessl_scanner"
    description: str = (
        "Scans a skill file or directory using tessl and returns a security score "
        "along with findings. Use this to evaluate the security posture of skills "
        "present in the repository. Input should be a file path or directory path."
    )
    args_schema: Type[TesslScanInput] = TesslScanInput

    def _prepare_skills_dir(self, path: str) -> list[str]:
        """
        Reorganize flat .md files in a skills directory into the structure
        tessl expects: <skills_dir>/<skill_name>/SKILL.md

        Files already inside a subdirectory are left untouched.
        Returns a list of prepared skill directories.
        """
        prepared = []
        SCRIPT_DIR = "/home/user1/aiproject/"
        repo_path = os.path.join(SCRIPT_DIR, "repo")
        skills_path = os.path.join(repo_path, "skills")
        for skill in os.listdir(skills_path):
            #entry_path = reposkills_path
            if skill.endswith(".md"):
                skill_name = os.path.splitext(skill)[0]
                skill_dir = os.path.join(skills_path, skill_name)
                os.makedirs(skill_dir, exist_ok=True)
                shutil.copy2(skills_path, os.path.join(skill_dir, "SKILL.md"))
                print(f"  Prepared skill: {skill_name}/SKILL.md")
                prepared.append(skill_dir)
        return prepared

    def _run(
        self,
        path: str,
        #run_manager: = None,
    ) -> str:
        """
        Execute a tessl scan on the given path.

        Args:
            path: Path to the file or directory to scan
            run_manager: Optional callback manager

        Returns:
            str: Tessl scan results with score and findings
        """
        try:
            if not os.path.exists(path):
                return f"[Error]: Path does not exist: {path}"

            scan_targets = []
            if os.path.isdir(path):
                scan_targets = self._prepare_skills_dir(path)
                if not scan_targets:
                    return f"[Tessl Scan]: No .md skill files found in directory: {path}"
            else:
                scan_targets = [path]

            all_results = []
            for target in scan_targets:
                result = subprocess.run(
                    ["tessl", "scan", target, "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                output = result.stdout.strip()
                stderr = result.stderr.strip()

                if result.returncode not in (0, 1):
                    all_results.append(
                        f"[Error scanning {target}] (exit {result.returncode}):\n{stderr or output}"
                    )
                elif not output:
                    all_results.append(f"[No output for {target}]\n{stderr}")
                else:
                    all_results.append(f"[Results for {target}]\n{output}")

            return "\n\n".join(all_results)

        except FileNotFoundError:
            return (
                "[Error]: tessl CLI not found. Ensure tessl is installed and available "
                "in PATH (https://tessl.io)."
            )
        except subprocess.TimeoutExpired:
            return f"[Error]: tessl scan timed out after 120 seconds for path: {path}"
        except Exception as e:
            return f"[Error]: tessl scan failed: {e}"
