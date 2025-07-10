import requests
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union

# ANSI color codes for terminal output
class LogColors:
    DEBUG = '\033[36m'      # Cyan
    INFO = '\033[32m'       # Green
    WARNING = '\033[33m'    # Yellow
    ERROR = '\033[31m'      # Red
    CRITICAL = '\033[35m'   # Magenta
    RESET = '\033[0m'       # Reset to default

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels"""

    def format(self, record):
        # Save the original format
        original_format = self._style._fmt

        # Color map for different log levels
        color_map = {
            logging.DEBUG: LogColors.DEBUG,
            logging.INFO: LogColors.INFO,
            logging.WARNING: LogColors.WARNING,
            logging.ERROR: LogColors.ERROR,
            logging.CRITICAL: LogColors.CRITICAL
        }

        # Get the color for this log level
        color = color_map.get(record.levelno, LogColors.RESET)

        # Apply color to the entire log message
        colored_format = f"{color}{original_format}{LogColors.RESET}"
        self._style._fmt = colored_format

        # Format the record
        formatted = super().format(record)

        # Restore original format
        self._style._fmt = original_format

        return formatted

# Configure logging with verbose format and colors
def setup_colored_logging():
    """Setup colored logging configuration"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create colored formatter
    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    return logger

# Initialize colored logging
logger = setup_colored_logging()

FIGMA_ACCESS_TOKEN: Optional[str] = os.environ.get("FIGMA_ACCESS_TOKEN", None)

def get_access_token() -> str:
    """
    Get the Figma access token from global constant or prompt the user.
    """
    logger.debug("Getting Figma access token")
    token = FIGMA_ACCESS_TOKEN
    if not token:
        logger.info("No token found in environment, prompting user")
        token = input("Enter your Figma access token: ").strip()
        if not token:
            logger.error("No token provided")
            raise ValueError("Figma access token is required to use this script.")
    logger.debug("Token obtained successfully")
    return token

def figma_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
    """
    Generic GET request to the Figma API with retries.
    """
    token = get_access_token()
    url = f"https://api.figma.com/v1/{endpoint}"
    headers = {
        "X-Figma-Token": token
    }

    logger.info(f"Making API request to: {url}")
    if params:
        logger.debug(f"Request params: {json.dumps(params)}")

    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}")
            resp = requests.get(url, headers=headers, params=params)
            logger.debug(f"Response status code: {resp.status_code}")

            if resp.status_code == 200:
                logger.info(f"Request to {endpoint} successful")
                logger.debug(f"Response headers: {dict(resp.headers)}")
                response_data = resp.json()
                logger.debug(f"Received {len(json.dumps(response_data))} bytes of data")
                return response_data
            elif resp.status_code == 429:  # Rate limited
                retry_after = int(resp.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Waiting for {retry_after} seconds before retry...")
                time.sleep(retry_after)
                continue
            else:
                logger.error(f"API Error: {resp.status_code} - {resp.text}")
                return {"error": True, "status_code": resp.status_code, "message": resp.text}
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info(f"Retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                logger.error(f"Max retries exceeded for {endpoint}")
                return {"error": True, "status_code": 0, "message": str(e)}

    logger.error(f"All {max_retries} attempts to {endpoint} failed")
    return {"error": True, "status_code": 0, "message": "Max retries exceeded"}

def get_user_info() -> Dict[str, Any]:
    """
    Get the current user's information including teams they belong to.

    Returns:
        dict: JSON response containing user data
    """
    logger.info("Fetching user information")
    response = figma_api_get("me")
    if not response.get("error"):
        logger.info(f"Successfully retrieved user info for: {response.get('handle', 'unknown')}")
    else:
        logger.error(f"Failed to retrieve user info: {response.get('message')}")
    return response

def get_team_projects(team_id: str) -> Dict[str, Any]:
    """
    Get all projects in a specific team.

    Args:
        team_id (str): The Figma team ID

    Returns:
        dict: JSON response containing all projects in the team
    """
    logger.info(f"Fetching projects for team {team_id}")
    response = figma_api_get(f"teams/{team_id}/projects")
    if not response.get("error"):
        projects = response.get("projects", [])
        logger.info(f"Successfully retrieved {len(projects)} projects for team {team_id}")
    else:
        logger.error(f"Failed to retrieve projects for team {team_id}: {response.get('message')}")
    return response

def get_files(project_id: str) -> Dict[str, Any]:
    """
    Get all files in a specific project.

    Args:
        project_id (str): The Figma project ID

    Returns:
        dict: JSON response containing all files in the project
    """
    logger.info(f"Fetching files for project {project_id}")
    response = figma_api_get(f"projects/{project_id}/files")
    if not response.get("error"):
        files = response.get("files", [])
        logger.info(f"Successfully retrieved {len(files)} files for project {project_id}")
    else:
        logger.error(f"Failed to retrieve files for project {project_id}: {response.get('message')}")
    return response

def get_pages(file_key: str) -> List[Dict[str, Any]]:
    """
    Get all pages in a specific file.

    Args:
        file_key (str): The Figma file key

    Returns:
        list: List of page objects containing id, name, and other metadata
    """
    logger.info(f"Fetching pages for file {file_key}")
    response = figma_api_get(f"files/{file_key}")

    if response and not response.get("error"):
        # Extract pages from the document structure
        document = response.get("document", {})
        children = document.get("children", [])
        logger.debug(f"File contains a document with {len(children)} top-level nodes")

        # Filter for nodes that are pages (top-level frames in Figma)
        pages: List[Dict[str, Any]] = []
        for child in children:
            if child.get("type") == "CANVAS":
                pages.append({
                    "id": child.get("id"),
                    "name": child.get("name"),
                    "type": child.get("type"),
                    "children_count": len(child.get("children", [])),
                    "background_color": child.get("backgroundColor", None)
                })
                logger.debug(f"Found page: {child.get('name')} with {len(child.get('children', []))} elements")

        logger.info(f"Successfully extracted {len(pages)} pages from file {file_key}")
        return pages
    else:
        logger.error(f"Failed to retrieve file {file_key}: {response.get('message')}")
        return []

def save_teams_to_json(output_dir: str = "data") -> str:
    """
    Fetch all teams and save them to a JSON file.
    Note: Uses the /me endpoint to get user info which contains team data.

    Args:
        output_dir (str): Directory to save the JSON file (created if doesn't exist)

    Returns:
        str: Path to the saved JSON file or error message
    """
    logger.info(f"Starting save_teams_to_json to directory: {output_dir}")
    try:
        logger.debug("Calling get_teams() which uses /me endpoint")
        teams_data = get_teams()

        if teams_data.get("error"):
            error_msg = f"Error fetching teams: {teams_data.get('message')}"
            logger.error(error_msg)
            return error_msg

        # Create output directory if it doesn't exist
        logger.debug(f"Creating directory if it doesn't exist: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = int(time.time())
        filename = os.path.join(output_dir, f"teams_{timestamp}.json")
        logger.info(f"Will save data to file: {filename}")

        # Write the JSON data to file
        logger.debug(f"Writing {len(json.dumps(teams_data))} bytes to file")
        with open(filename, 'w') as f:
            json.dump(teams_data, f, indent=2)

        success_msg = f"Teams data successfully saved to {filename}"
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to save teams data: {str(e)}"
        logger.exception(error_msg)
        return error_msg

def save_team_to_json(team_id: str, team_data: Dict[str, Any], output_dir: str = "data") -> str:
    """
    Save individual team data to a JSON file.

    Args:
        team_id (str): The team ID
        team_data (dict): The team data to save
        output_dir (str): Directory to save the JSON file

    Returns:
        str: Path to the saved JSON file or error message
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create filename with team ID and timestamp
        timestamp = int(time.time())
        filename = os.path.join(output_dir, f"team_{team_id}_{timestamp}.json")
        logger.info(f"Saving team {team_id} to file: {filename}")

        # Write the JSON data to file
        with open(filename, 'w') as f:
            json.dump(team_data, f, indent=2)

        success_msg = f"Team {team_id} data saved to {filename}"
        logger.info(success_msg)
        return filename

    except Exception as e:
        error_msg = f"Failed to save team {team_id} data: {str(e)}"
        logger.exception(error_msg)
        return error_msg

def get_teams_from_file(team_ids_file: str = "team_ids") -> Dict[str, Any]:
    """
    Get team information for team IDs listed in a file.
    Each line in the file should contain one team ID.

    Args:
        team_ids_file (str): Path to file containing team IDs (one per line)

    Returns:
        dict: Combined response containing all teams data
    """
    logger.info(f"Reading team IDs from file: {team_ids_file}")

    try:
        # Read team IDs from file
        if not os.path.exists(team_ids_file):
            error_msg = f"Team IDs file not found: {team_ids_file}"
            logger.error(error_msg)
            return {"error": True, "message": error_msg}

        team_ids = []
        with open(team_ids_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                team_id = line.strip()
                if team_id and not team_id.startswith('#'):  # Skip empty lines and comments
                    team_ids.append(team_id)
                    logger.debug(f"Line {line_num}: Added team ID {team_id}")
                elif team_id.startswith('#'):
                    logger.debug(f"Line {line_num}: Skipped comment line")
                else:
                    logger.debug(f"Line {line_num}: Skipped empty line")

        logger.info(f"Found {len(team_ids)} team IDs in file")

        if not team_ids:
            error_msg = f"No valid team IDs found in {team_ids_file}"
            logger.warning(error_msg)
            return {"error": True, "message": error_msg}

        # Process results summary
        results = {
            "source": f"file: {team_ids_file}",
            "total_teams": len(team_ids),
            "processed_teams": [],
            "successful_teams": 0,
            "failed_teams": 0
        }

        return {"team_ids": team_ids, "results": results}

    except Exception as e:
        error_msg = f"Failed to process teams from file {team_ids_file}: {str(e)}"
        logger.exception(error_msg)
        return {"error": True, "message": error_msg}

def save_teams_from_file_to_json(team_ids_file: str = "team_ids", output_dir: str = "data") -> str:
    """
    Read team IDs from file and save each team's data to individual JSON files.

    Args:
        team_ids_file (str): Path to file containing team IDs (one per line)
        output_dir (str): Directory to save the JSON files (created if doesn't exist)

    Returns:
        str: Summary message of the operation
    """
    logger.info(f"Starting save_teams_from_file_to_json with file: {team_ids_file}")

    try:
        # Get team IDs from file
        file_data = get_teams_from_file(team_ids_file)

        if file_data.get("error"):
            error_msg = f"Error reading teams from file: {file_data.get('message')}"
            logger.error(error_msg)
            return error_msg

        team_ids = file_data.get("team_ids", [])
        results = file_data.get("results", {})

        # Create output directory if it doesn't exist
        logger.debug(f"Creating directory if it doesn't exist: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        # Process each team individually
        saved_files = []

        for i, team_id in enumerate(team_ids, 1):
            logger.info(f"Processing team {i}/{len(team_ids)}: {team_id}")

            # Get team projects (this gives us team info + projects)
            team_response = get_team_projects(team_id)

            if not team_response.get("error"):
                team_data = {
                    "id": team_id,
                    "projects": team_response.get("projects", []),
                    "project_count": len(team_response.get("projects", [])),
                    "fetched_at": time.time(),
                    "source": team_ids_file
                }

                # Save individual team file
                saved_file = save_team_to_json(team_id, team_data, output_dir)
                if not saved_file.startswith("Failed"):
                    saved_files.append(saved_file)
                    results["successful_teams"] += 1
                    logger.info(f"Successfully processed team {team_id} with {team_data['project_count']} projects")
                else:
                    results["failed_teams"] += 1
                    logger.error(f"Failed to save team {team_id}: {saved_file}")

                results["processed_teams"].append({
                    "id": team_id,
                    "status": "success" if not saved_file.startswith("Failed") else "save_failed",
                    "project_count": team_data["project_count"],
                    "file": saved_file if not saved_file.startswith("Failed") else None
                })
            else:
                logger.error(f"Failed to get data for team {team_id}: {team_response.get('message')}")
                results["failed_teams"] += 1

                # Save error info to file as well
                error_data = {
                    "id": team_id,
                    "error": True,
                    "message": team_response.get("message"),
                    "projects": [],
                    "project_count": 0,
                    "fetched_at": time.time(),
                    "source": team_ids_file
                }

                saved_file = save_team_to_json(team_id, error_data, output_dir)
                if not saved_file.startswith("Failed"):
                    saved_files.append(saved_file)

                results["processed_teams"].append({
                    "id": team_id,
                    "status": "api_error",
                    "error": team_response.get("message"),
                    "file": saved_file if not saved_file.startswith("Failed") else None
                })

        # Save summary file
        summary_data = {
            "summary": results,
            "files_created": saved_files,
            "timestamp": time.time()
        }

        summary_filename = os.path.join(output_dir, f"teams_summary_{int(time.time())}.json")
        with open(summary_filename, 'w') as f:
            json.dump(summary_data, f, indent=2)

        success_msg = (f"Processed {len(team_ids)} teams: "
                      f"{results['successful_teams']} successful, "
                      f"{results['failed_teams']} failed. "
                      f"Created {len(saved_files)} files. "
                      f"Summary saved to {summary_filename}")

        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to save teams data from file: {str(e)}"
        logger.exception(error_msg)
        return error_msg

def save_project_files_to_json(project_id: str, project_data: Dict[str, Any], output_dir: str = "data") -> str:
    """
    Save individual project files data to a JSON file.

    Args:
        project_id (str): The project ID
        project_data (dict): The project files data to save
        output_dir (str): Directory to save the JSON file

    Returns:
        str: Path to the saved JSON file or error message
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create filename with project ID and timestamp
        timestamp = int(time.time())
        filename = os.path.join(output_dir, f"project_files_{project_id}_{timestamp}.json")
        logger.info(f"Saving project {project_id} files to file: {filename}")

        # Write the JSON data to file
        with open(filename, 'w') as f:
            json.dump(project_data, f, indent=2)

        success_msg = f"Project {project_id} files data saved to {filename}"
        logger.info(success_msg)
        return filename

    except Exception as e:
        error_msg = f"Failed to save project {project_id} files data: {str(e)}"
        logger.exception(error_msg)
        return error_msg

def save_teams_with_project_files_to_json(team_ids_file: str = "team_ids", output_dir: str = "data") -> str:
    """
    Read team IDs from file and save each team's data with all project files to individual JSON files.

    Args:
        team_ids_file (str): Path to file containing team IDs (one per line)
        output_dir (str): Directory to save the JSON files (created if doesn't exist)

    Returns:
        str: Summary message of the operation
    """
    logger.info(f"Starting save_teams_with_project_files_to_json with file: {team_ids_file}")

    try:
        # Get team IDs from file
        file_data = get_teams_from_file(team_ids_file)

        if file_data.get("error"):
            error_msg = f"Error reading teams from file: {file_data.get('message')}"
            logger.error(error_msg)
            return error_msg

        team_ids = file_data.get("team_ids", [])
        results = file_data.get("results", {})

        # Create output directory if it doesn't exist
        logger.debug(f"Creating directory if it doesn't exist: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        # Process each team individually
        saved_files = []
        total_projects = 0
        total_files = 0

        for i, team_id in enumerate(team_ids, 1):
            logger.info(f"Processing team {i}/{len(team_ids)}: {team_id}")

            # Get team projects
            team_response = get_team_projects(team_id)

            if not team_response.get("error"):
                projects = team_response.get("projects", [])
                team_projects_with_files = []

                logger.info(f"Found {len(projects)} projects in team {team_id}")
                total_projects += len(projects)

                # Get files for each project
                for j, project in enumerate(projects, 1):
                    project_id = project.get("id")
                    project_name = project.get("name", "Unknown")

                    logger.info(f"Processing project {j}/{len(projects)}: {project_name} ({project_id})")

                    # Get files in this project
                    files_response = get_files(project_id)

                    if not files_response.get("error"):
                        files = files_response.get("files", [])
                        logger.info(f"Found {len(files)} files in project {project_name}")
                        total_files += len(files)

                        project_with_files = {
                            "id": project_id,
                            "name": project_name,
                            "files": files,
                            "file_count": len(files),
                            "fetched_at": time.time()
                        }

                        # Save individual project files to separate JSON
                        project_file_data = {
                            "project": project_with_files,
                            "team_id": team_id,
                            "source": team_ids_file
                        }

                        saved_file = save_project_files_to_json(project_id, project_file_data, output_dir)
                        if not saved_file.startswith("Failed"):
                            saved_files.append(saved_file)

                        team_projects_with_files.append(project_with_files)
                    else:
                        logger.error(f"Failed to get files for project {project_name}: {files_response.get('message')}")
                        project_with_files = {
                            "id": project_id,
                            "name": project_name,
                            "error": True,
                            "message": files_response.get("message"),
                            "files": [],
                            "file_count": 0,
                            "fetched_at": time.time()
                        }
                        team_projects_with_files.append(project_with_files)

                # Save team data with all projects and their files
                team_data = {
                    "id": team_id,
                    "projects": team_projects_with_files,
                    "project_count": len(team_projects_with_files),
                    "total_files": sum(p.get("file_count", 0) for p in team_projects_with_files),
                    "fetched_at": time.time(),
                    "source": team_ids_file
                }

                # Save individual team file
                saved_file = save_team_to_json(team_id, team_data, output_dir)
                if not saved_file.startswith("Failed"):
                    saved_files.append(saved_file)
                    results["successful_teams"] += 1
                    logger.info(f"Successfully processed team {team_id} with {team_data['project_count']} projects and {team_data['total_files']} files")
                else:
                    results["failed_teams"] += 1
                    logger.error(f"Failed to save team {team_id}: {saved_file}")

                results["processed_teams"].append({
                    "id": team_id,
                    "status": "success" if not saved_file.startswith("Failed") else "save_failed",
                    "project_count": team_data["project_count"],
                    "file_count": team_data["total_files"],
                    "file": saved_file if not saved_file.startswith("Failed") else None
                })
            else:
                logger.error(f"Failed to get data for team {team_id}: {team_response.get('message')}")
                results["failed_teams"] += 1

                # Save error info to file as well
                error_data = {
                    "id": team_id,
                    "error": True,
                    "message": team_response.get("message"),
                    "projects": [],
                    "project_count": 0,
                    "total_files": 0,
                    "fetched_at": time.time(),
                    "source": team_ids_file
                }

                saved_file = save_team_to_json(team_id, error_data, output_dir)
                if not saved_file.startswith("Failed"):
                    saved_files.append(saved_file)

                results["processed_teams"].append({
                    "id": team_id,
                    "status": "api_error",
                    "error": team_response.get("message"),
                    "file": saved_file if not saved_file.startswith("Failed") else None
                })

        # Save summary file
        summary_data = {
            "summary": results,
            "total_projects": total_projects,
            "total_files": total_files,
            "files_created": saved_files,
            "timestamp": time.time()
        }

        summary_filename = os.path.join(output_dir, f"teams_with_files_summary_{int(time.time())}.json")
        with open(summary_filename, 'w') as f:
            json.dump(summary_data, f, indent=2)

        success_msg = (f"Processed {len(team_ids)} teams with {total_projects} projects and {total_files} files: "
                      f"{results['successful_teams']} successful teams, "
                      f"{results['failed_teams']} failed teams. "
                      f"Created {len(saved_files)} files. "
                      f"Summary saved to {summary_filename}")

        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to save teams data with project files from file: {str(e)}"
        logger.exception(error_msg)
        return error_msg

def save_all_data_to_single_json(team_ids_file: str = "team_ids", output_dir: str = "data") -> str:
    """
    Read team IDs from file and save all teams, projects, and files data to a single consolidated JSON file.

    Args:
        team_ids_file (str): Path to file containing team IDs (one per line)
        output_dir (str): Directory to save the JSON file (created if doesn't exist)

    Returns:
        str: Path to the saved JSON file or error message
    """
    logger.info(f"Starting save_all_data_to_single_json with file: {team_ids_file}")

    try:
        # Get team IDs from file
        file_data = get_teams_from_file(team_ids_file)

        if file_data.get("error"):
            error_msg = f"Error reading teams from file: {file_data.get('message')}"
            logger.error(error_msg)
            return error_msg

        team_ids = file_data.get("team_ids", [])

        # Create output directory if it doesn't exist
        logger.debug(f"Creating directory if it doesn't exist: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        # Initialize consolidated data structure
        consolidated_data = {
            "metadata": {
                "source": team_ids_file,
                "total_teams": len(team_ids),
                "fetched_at": time.time(),
                "successful_teams": 0,
                "failed_teams": 0,
                "total_projects": 0,
                "total_files": 0
            },
            "teams": []
        }

        # Process each team individually
        for i, team_id in enumerate(team_ids, 1):
            logger.info(f"Processing team {i}/{len(team_ids)}: {team_id}")

            # Get team projects
            team_response = get_team_projects(team_id)

            if not team_response.get("error"):
                projects = team_response.get("projects", [])
                team_projects_with_files = []

                logger.info(f"Found {len(projects)} projects in team {team_id}")
                consolidated_data["metadata"]["total_projects"] += len(projects)

                # Get files for each project
                for j, project in enumerate(projects, 1):
                    project_id = project.get("id")
                    project_name = project.get("name", "Unknown")

                    logger.info(f"Processing project {j}/{len(projects)}: {project_name} ({project_id})")

                    # Get files in this project
                    files_response = get_files(project_id)

                    if not files_response.get("error"):
                        files = files_response.get("files", [])
                        logger.info(f"Found {len(files)} files in project {project_name}")
                        consolidated_data["metadata"]["total_files"] += len(files)

                        project_with_files = {
                            "id": project_id,
                            "name": project_name,
                            "files": files,
                            "file_count": len(files),
                            "fetched_at": time.time()
                        }

                        team_projects_with_files.append(project_with_files)
                    else:
                        logger.error(f"Failed to get files for project {project_name}: {files_response.get('message')}")
                        project_with_files = {
                            "id": project_id,
                            "name": project_name,
                            "error": True,
                            "message": files_response.get("message"),
                            "files": [],
                            "file_count": 0,
                            "fetched_at": time.time()
                        }
                        team_projects_with_files.append(project_with_files)

                # Add team data to consolidated structure
                team_data = {
                    "id": team_id,
                    "status": "success",
                    "projects": team_projects_with_files,
                    "project_count": len(team_projects_with_files),
                    "total_files": sum(p.get("file_count", 0) for p in team_projects_with_files),
                    "fetched_at": time.time()
                }

                consolidated_data["teams"].append(team_data)
                consolidated_data["metadata"]["successful_teams"] += 1
                logger.info(f"Successfully processed team {team_id} with {team_data['project_count']} projects and {team_data['total_files']} files")

            else:
                logger.error(f"Failed to get data for team {team_id}: {team_response.get('message')}")
                consolidated_data["metadata"]["failed_teams"] += 1

                # Add error team data to consolidated structure
                error_team_data = {
                    "id": team_id,
                    "status": "error",
                    "error": True,
                    "message": team_response.get("message"),
                    "projects": [],
                    "project_count": 0,
                    "total_files": 0,
                    "fetched_at": time.time()
                }

                consolidated_data["teams"].append(error_team_data)

        # Create consolidated filename with timestamp
        timestamp = int(time.time())
        filename = os.path.join(output_dir, f"figma_consolidated_data_{timestamp}.json")
        logger.info(f"Saving consolidated data to file: {filename}")

        # Write the consolidated JSON data to file
        logger.debug(f"Writing {len(json.dumps(consolidated_data))} bytes to consolidated file")
        with open(filename, 'w') as f:
            json.dump(consolidated_data, f, indent=2)

        success_msg = (f"Consolidated data saved to {filename}. "
                      f"Processed {consolidated_data['metadata']['total_teams']} teams: "
                      f"{consolidated_data['metadata']['successful_teams']} successful, "
                      f"{consolidated_data['metadata']['failed_teams']} failed. "
                      f"Total: {consolidated_data['metadata']['total_projects']} projects, "
                      f"{consolidated_data['metadata']['total_files']} files.")

        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to save consolidated data: {str(e)}"
        logger.exception(error_msg)
        return error_msg


if __name__ == "__main__":
    logger.info("Script started")

    # Check if team_ids file exists and use it, otherwise use the /me endpoint
    if os.path.exists("team_ids"):
        logger.info("Found team_ids file, creating consolidated JSON with all data")
        result = save_all_data_to_single_json()
    else:
        logger.info("No team_ids file found, using /me endpoint")
        result = save_teams_to_json()

    print(result)
    logger.info("Script completed")
