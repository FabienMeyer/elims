# Documentation Deployment

This project uses [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) with [mike](https://github.com/jimporter/mike) for versioned documentation deployment to GitHub Pages.

## Documentation Structure

```
docs/
├── index.md              # Homepage
├── ci-cd.md             # CI/CD documentation
├── release-notes.md     # Release notes
├── contributing.md      # Contributing guide
├── code_of_conduct.md   # Code of conduct
├── license.md           # License
├── privacy.md           # Privacy policy
├── assets/              # Images and static files
├── js/                  # JavaScript files
└── stylesheets/         # CSS files
```

## Automatic Deployment

Documentation is automatically deployed to GitHub Pages in these scenarios:

### 1. **Development Docs (Latest)**

- **Trigger**: Push to `main` or `master` branch
- **Version**: `dev` and `latest`
- **URL**: `https://yourusername.github.io/elims2/latest/`
- Automatically updates with every commit to main

### 2. **Release Docs (Stable)**

- **Trigger**: Publishing a GitHub Release
- **Version**: Release tag (e.g., `v1.0.0`) and `stable`
- **URL**: `https://yourusername.github.io/elims2/stable/`
- Creates a permanent versioned copy

### 3. **Manual Deployment**

- **Trigger**: Manually run workflow
- **Version**: `dev`
- Use when you need to force a rebuild

## Version Management

### Available Versions

The documentation is versioned as follows:

- **`latest`** - Latest development version from main branch
- **`stable`** - Latest stable release
- **`v1.0.0`, `v1.1.0`, etc.** - Specific release versions

### Version Selector

Users can switch between versions using the version selector in the documentation header.

## Local Development

### Prerequisites

Install MkDocs and required plugins:

```bash
# Using uv (recommended)
uv tool install mkdocs-material
uv tool install mike
uv tool install mkdocs-minify-plugin
uv tool install mkdocs-glightbox
uv tool install mkdocstrings[python]

# Or using pip
pip install mkdocs-material mike mkdocs-minify-plugin mkdocs-glightbox mkdocstrings[python]
```

### Serve Locally

Start a local development server:

```bash
mkdocs serve
```

Visit: http://localhost:8000

The server auto-reloads when you save changes.

### Build Locally

Build the static site:

```bash
mkdocs build
```

Output goes to `site/` directory.

## Manual Version Management

### Deploy a New Version

```bash
# Deploy a specific version
mike deploy v1.0.0

# Deploy and set as default
mike deploy v1.0.0 stable --update-aliases --push

# Deploy development version
mike deploy dev latest --update-aliases --push
```

### List All Versions

```bash
mike list
```

### Delete a Version

```bash
mike delete v0.9.0 --push
```

### Set Default Version

```bash
mike set-default stable --push
```

## 📝 Writing Documentation

### Adding New Pages

1. Create a new `.md` file in `docs/`
1. Add it to `nav` section in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Your New Page: your-page.md
```

### Markdown Features

The documentation supports:

- **Admonitions** (notes, warnings, tips)
- **Code blocks** with syntax highlighting
- **Mermaid diagrams**
- **Plotly charts**
- **Math equations** (KaTeX)
- **Tabbed content**
- **Task lists**
- **Emoji** 🎉
- **Tables**
- **Footnotes**

### Code Documentation

Use `mkdocstrings` to auto-generate API docs from docstrings:

```markdown
::: module.path.ClassName
    options:
      show_source: true
      show_root_heading: true
```

### Admonitions Example

```markdown
!!! note "Note Title"
    This is a note

!!! warning
    This is a warning

!!! tip
    This is a tip

!!! danger
    This is dangerous
```

### Mermaid Diagrams

````markdown
```mermaid
graph LR
    A[Start] --> B[Process]
    B --> C[End]
```
````

## 🎨 Customization

### Theme Configuration

Edit `mkdocs.yml` to customize:

- Colors and fonts
- Navigation structure
- Features (search, tabs, etc.)
- Logo and favicon
- Social links

### Custom CSS

Add styles to `docs/stylesheets/extra.css`

### Custom JavaScript

Add scripts to `docs/js/`

## 🔐 Required GitHub Settings

### Enable GitHub Pages

1. Go to repository **Settings > Pages**
1. Source: **Deploy from a branch**
1. Branch: **gh-pages** / **root**
1. Click **Save**

### Workflow Permissions

1. Go to **Settings > Actions > General**
1. Workflow permissions: **Read and write permissions**
1. Check **Allow GitHub Actions to create and approve pull requests**
1. Click **Save**

## 🏷️ Release Workflow

When you publish a new release:

1. **Create a tag**:

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

1. **Publish the release** on GitHub

1. **Documentation is auto-deployed** with:

   - Version: `v1.0.0`
   - Alias: `stable`
   - Appears in version selector

## 📊 Documentation Status

Add this badge to your README:

```markdown
[![Documentation](https://img.shields.io/badge/docs-stable-blue.svg)](https://yourusername.github.io/elims2/)
```

## 🐛 Troubleshooting

### Build Fails

**Check Python version**:

```bash
python --version  # Should be 3.13+
```

**Reinstall dependencies**:

```bash
uv tool install --force mkdocs-material
```

### Versions Not Showing

**Check gh-pages branch**:

```bash
git fetch origin
git branch -r | grep gh-pages
```

**Manually list versions**:

```bash
git checkout gh-pages
mike list
```

### Local Server Issues

**Clear cache**:

```bash
rm -rf site/
mkdocs serve --clean
```

### Permission Errors

Ensure workflow has write permissions in repository settings.

## 📚 Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Mike Documentation](https://github.com/jimporter/mike)
- [MkDocs Plugins](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins)
- [Markdown Guide](https://www.markdownguide.org/)

## 💡 Tips

1. **Preview before pushing**: Always check locally with `mkdocs serve`
1. **Use branches**: Create feature branches for large doc changes
1. **Keep it simple**: Write clear, concise documentation
1. **Add examples**: Code examples help users understand
1. **Update regularly**: Keep docs in sync with code changes
1. **Use admonitions**: Highlight important information
1. **Link internally**: Use relative links between pages
1. **Version wisely**: Only create new versions for significant releases
