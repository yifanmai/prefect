"""
Interface for creating and reading artifacts.
"""

import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from prefect._internal.compatibility.experimental import experimental
from prefect.client.orchestration import PrefectClient
from prefect.client.utilities import inject_client
from prefect.context import FlowRunContext, TaskRunContext
from prefect.server.schemas.actions import ArtifactCreate
from prefect.utilities.asyncutils import sync_compatible


@inject_client
@experimental(
    feature="The artifacts feature",
    group="artifacts",
)
async def _create_artifact(
    type: str,
    key: Optional[str] = None,
    description: Optional[str] = None,
    data: Optional[Union[Dict[str, Any], Any]] = None,
    client: Optional[PrefectClient] = None,
) -> UUID:
    """
    Helper function to create an artifact.

    Args:
        - type:  A string identifying the type of artifact.
        - key: A string user-provided identifier.
        - description: A user-specified description of the artifact.
        - data: A JSON payload that allows for a result to be retrieved.

    Returns:
        - The table artifact ID.
    """
    artifact_args = {}
    task_run_ctx = TaskRunContext.get()
    flow_run_ctx = FlowRunContext.get()

    if task_run_ctx:
        artifact_args["task_run_id"] = task_run_ctx.task_run.id
        artifact_args["flow_run_id"] = task_run_ctx.task_run.flow_run_id
    elif flow_run_ctx:
        artifact_args["flow_run_id"] = flow_run_ctx.flow_run.id

    if key is not None:
        artifact_args["key"] = key
    if type is not None:
        artifact_args["type"] = type
    if description is not None:
        artifact_args["description"] = description
    if data is not None:
        artifact_args["data"] = data

    artifact = ArtifactCreate(**artifact_args)

    return await client.create_artifact(artifact=artifact)


@sync_compatible
async def create_link_artifact(
    link: str,
    link_text: Optional[str] = None,
    key: Optional[str] = None,
    description: Optional[str] = None,
) -> UUID:
    """
    Create a link artifact.

    Args:
        - link: The link to create.

    Returns:
        - The table artifact ID.
    """
    formatted_link = f"[{link_text}]({link})" if link_text else f"[{link}]({link})"
    artifact = await _create_artifact(
        key=key,
        type="markdown",
        description=description,
        data=formatted_link,
    )

    return artifact.id


@sync_compatible
async def create_markdown_artifact(
    markdown: str,
    key: Optional[str] = None,
    description: Optional[str] = None,
) -> UUID:
    """
    Create a markdown artifact.

    Args:
        - markdown: The markdown to create.

    Returns:
        - The table artifact ID.
    """
    artifact = await _create_artifact(
        key=key,
        type="markdown",
        description=description,
        data=markdown,
    )

    return artifact.id


@sync_compatible
async def create_table_artifact(
    table: Union[Dict[str, List[Any]], List[Dict[str, Any]]],
    key: Optional[str] = None,
    description: Optional[str] = None,
) -> UUID:
    """
    Create a table artifact.

    Args:
        - table: The table to create.

    Returns:
        - The table artifact ID.
    """
    formatted_table = json.dumps(table) if isinstance(table, list) else table

    artifact = await _create_artifact(
        key=key,
        type="table",
        description=description,
        data=formatted_table,
    )

    return artifact.id
