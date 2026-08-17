import os
import sys
from typing import Dict, List, Optional

PLUGIN_RESOURCES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cpi-timber-plugin", "CPI_TIMBER"))
if PLUGIN_RESOURCES_PATH not in sys.path:
    sys.path.append(PLUGIN_RESOURCES_PATH)

from resources.cpi_coda import CodaClient


def list_folders(api_token: str, workspace_id: Optional[str] = None) -> List[Dict[str, str]]:
    return CodaClient(api_token).list_folders(workspace_id=workspace_id)


def find_folder_by_name(
    api_token: str,
    folder_name: str,
    workspace_id: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    return CodaClient(api_token).find_folder_by_name(folder_name, workspace_id=workspace_id)


def get_docs_in_folder(api_token: str, folder_id: str) -> List[Dict[str, str]]:
    return CodaClient(api_token).get_docs_in_folder(folder_id)


def get_active_folder_docs(
    api_token: str,
    folder_name: str = "ACTIVE",
    workspace_id: Optional[str] = None,
) -> List[Dict[str, str]]:
    return CodaClient(api_token).get_active_folder_docs(folder_name=folder_name, workspace_id=workspace_id)
