# Development and checks

The repository uses uv for the Python workspace and npm for the frontend. The canonical verification commands are defined in `.github/workflows/ci.yml`.

Run focused checks while developing, then run the complete relevant CI jobs before approval. Documentation must build in strict mode at the root and for every affected component.

The [command reference](command-reference.md) lists the supported commands by tool and workflow.
