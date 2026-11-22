"""Audit or reconcile ELIMS GitHub labels and Project configuration."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
GH = shutil.which("gh") or "gh"


def run_gh(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(  # noqa: S603 - argument arrays avoid a shell
        [GH, *args],
        input=input_text,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "GitHub CLI failed")
    return result.stdout


def graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables})
    output = run_gh("api", "graphql", "--input", "-", input_text=payload)
    response = json.loads(output)
    if response.get("errors"):
        raise RuntimeError(json.dumps(response["errors"], indent=2))
    return response["data"]


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def reconcile_labels(config: dict[str, Any], apply: bool) -> list[dict[str, Any]]:
    repo = config["repository"]
    current = {
        item["name"]: item
        for item in json.loads(
            run_gh("label", "list", "--repo", repo, "--limit", "1000", "--json", "name,color,description")
        )
    }
    operations: list[dict[str, Any]] = []
    for desired in config["labels"]:
        existing = current.get(desired["name"])
        matched = (
            existing
            and existing["color"].upper() == desired["color"].upper()
            and (existing.get("description") or "") == desired["description"]
        )
        if matched:
            continue
        action = "edit-label" if existing else "create-label"
        operations.append({"action": action, "name": desired["name"]})
        if apply:
            verb = "edit" if existing else "create"
            run_gh(
                "label",
                verb,
                desired["name"],
                "--repo",
                repo,
                "--color",
                desired["color"],
                "--description",
                desired["description"],
            )
    return operations


PROJECT_QUERY = """
query($login:String!,$number:Int!,$repo:String!){
  user(login:$login){
    projectV2(number:$number){
      id
      closed
      repositories(first:100){nodes{nameWithOwner}}
      fields(first:100){nodes{
        ... on ProjectV2FieldCommon{id name dataType}
        ... on ProjectV2SingleSelectField{options{id name}}
      }}
      workflows(first:100){nodes{name enabled}}
      views(first:100){nodes{id name layout filter
        fields(first:100){nodes{... on ProjectV2FieldCommon{id}}}
        groupByFields(first:10){nodes{... on ProjectV2FieldCommon{name}}}
        verticalGroupByFields(first:10){nodes{... on ProjectV2FieldCommon{name}}}
      }}
    }
  }
  repository(owner:$login,name:$repo){id nameWithOwner}
}
"""


STATUS_COLORS = ["GRAY", "BLUE", "YELLOW", "ORANGE", "PURPLE", "PINK", "GREEN", "GREEN", "GREEN", "RED"]


def project_state(owner: str, number: int, repo_name: str) -> dict[str, Any]:
    data = graphql(PROJECT_QUERY, {"login": owner, "number": number, "repo": repo_name})
    project = data["user"]["projectV2"]
    if not project:
        raise RuntimeError(f"Project {owner}/{number} was not found")
    project["repository"] = data["repository"]
    return project


def reconcile_project(config: dict[str, Any], apply: bool) -> list[dict[str, Any]]:
    repository = config["repository"]
    owner, repo_name = repository.split("/", 1)
    project_config = config["project"]
    if project_config["owner"] != owner:
        raise RuntimeError("Repository owner and Project owner must match")
    project = project_state(owner, int(project_config["number"]), repo_name)
    operations: list[dict[str, Any]] = []

    desired_closed = bool(project_config.get("closed", False))
    if project["closed"] != desired_closed:
        operations.append({"action": "set-project-closed", "value": desired_closed})
        if apply:
            graphql(
                "mutation($project:ID!,$closed:Boolean!){"
                "updateProjectV2(input:{projectId:$project,closed:$closed}){clientMutationId}}",
                {"project": project["id"], "closed": desired_closed},
            )

    linked = {item["nameWithOwner"] for item in project["repositories"]["nodes"]}
    if repository not in linked:
        operations.append({"action": "link-repository", "repository": repository})
        if apply:
            graphql(
                "mutation($project:ID!,$repository:ID!){"
                "linkProjectV2ToRepository(input:{projectId:$project,repositoryId:$repository}){repository{id}}}",
                {"project": project["id"], "repository": project["repository"]["id"]},
            )

    fields = {node["name"]: node for node in project["fields"]["nodes"]}
    status = fields.get(project_config["status-field"])
    if not status:
        raise RuntimeError(f"Missing Project field: {project_config['status-field']}")
    existing_options = {item["name"]: item for item in status.get("options", [])}
    desired_names = project_config["statuses"]
    if list(existing_options) != desired_names:
        operations.append({"action": "replace-status-options", "from": list(existing_options), "to": desired_names})
        if apply:
            options = []
            for index, name in enumerate(desired_names):
                option = {
                    "name": name,
                    "color": STATUS_COLORS[index],
                    "description": f"ELIMS workflow status: {name}",
                }
                if name in existing_options:
                    option["id"] = existing_options[name]["id"]
                options.append(option)
            graphql(
                "mutation($field:ID!,$options:[ProjectV2SingleSelectFieldOptionInput!]){"
                "updateProjectV2Field(input:{fieldId:$field,singleSelectOptions:$options}){"
                "projectV2Field{... on ProjectV2SingleSelectField{id}}}}",
                {"field": status["id"], "options": options},
            )

    workflows = {workflow["name"]: workflow["enabled"] for workflow in project["workflows"]["nodes"]}
    for name in project_config.get("enabled-workflows", []):
        if not workflows.get(name):
            operations.append({"action": "configure-workflow-in-project-settings", "name": name})
    views = {view["name"]: view for view in project["views"]["nodes"]}
    if "All work" not in views and "Status board" in views:
        view = views.pop("Status board")
        operations.append({"action": "rename-view", "from": "Status board", "to": "All work"})
        if apply:
            graphql(
                'mutation($id:ID!){updateProjectV2View(input:{viewId:$id,name:"All work"}){projectV2View{id}}}',
                {"id": view["id"]},
            )
        view["name"] = "All work"
        views["All work"] = view

    layout_map = {"board": "BOARD_LAYOUT", "table": "TABLE_LAYOUT", "roadmap": "ROADMAP_LAYOUT"}
    for desired in project_config["views"]:
        name = desired["name"]
        layout = layout_map[desired["layout"]]
        filter_value = desired.get("filter") or ""
        visible_ids = [fields[field]["id"] for field in desired["fields"]]
        existing = views.get(name)
        rename_from = desired.get("rename-from")
        if not existing and rename_from and rename_from in views:
            existing = views.pop(rename_from)
            operations.append({"action": "rename-view", "from": rename_from, "to": name})
            if apply:
                graphql(
                    "mutation($id:ID!,$name:String!){"
                    "updateProjectV2View(input:{viewId:$id,name:$name}){projectV2View{id}}}",
                    {"id": existing["id"], "name": name},
                )
            existing["name"] = name
            views[name] = existing
        if existing:
            current_filter = existing.get("filter") or ""
            grouping = "verticalGroupByFields" if layout == "BOARD_LAYOUT" else "groupByFields"
            groups = [field["name"] for field in existing[grouping]["nodes"]]
            expected_groups = [desired["group-by"]] if desired.get("group-by") else []
            if groups != expected_groups:
                operations.append({"action": "set-grouping-in-project-view", "name": name, "groups": expected_groups})
            current_fields = {field["id"] for field in existing["fields"]["nodes"]}
            if existing["layout"] == layout and current_filter == filter_value and current_fields == set(visible_ids):
                continue
            operations.append({"action": "update-view", "name": name})
            if apply:
                graphql(
                    "mutation($id:ID!,$layout:ProjectV2ViewLayout!,$filter:String!,$fields:[ID!]){updateProjectV2View(input:{viewId:$id,layout:$layout,filter:$filter,configuration:{visibleFieldIds:$fields}}){projectV2View{id}}}",
                    {"id": existing["id"], "layout": layout, "filter": filter_value, "fields": visible_ids},
                )
            continue
        operations.append({"action": "create-view", "name": name})
        if apply:
            result = graphql(
                "mutation($project:ID!,$name:String!,$layout:ProjectV2ViewLayout!,$fields:[ID!]){createProjectV2View(input:{projectId:$project,name:$name,layout:$layout,configuration:{visibleFieldIds:$fields}}){projectV2View{id}}}",
                {"project": project["id"], "name": name, "layout": layout, "fields": visible_ids},
            )
            view_id = result["createProjectV2View"]["projectV2View"]["id"]
            if filter_value:
                graphql(
                    "mutation($id:ID!,$filter:String!){updateProjectV2View(input:{viewId:$id,filter:$filter}){projectV2View{id}}}",
                    {"id": view_id, "filter": filter_value},
                )
    return operations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the reported reconciliation")
    args = parser.parse_args()
    labels = load_yaml(ROOT / ".github" / "labels.yml")
    project = load_yaml(ROOT / ".github" / "elims-project.yml")
    operations = reconcile_labels(labels, args.apply)
    operations.extend(reconcile_project(project, args.apply))
    manual = any(
        op["action"] in {"configure-workflow-in-project-settings", "set-grouping-in-project-view"} for op in operations
    )
    status = "manual-settings-needed" if manual else "applied" if args.apply else "planned"
    print(json.dumps({"status": status, "operations": operations}, indent=2))
    return 2 if manual or (operations and not args.apply) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, RuntimeError, ValueError, yaml.YAMLError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
