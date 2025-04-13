# Remote Workspace Index

This tool helps you create an index of your repository structure for easier navigation.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/amuzetnom02/research.git
   cd research
   ```

2. Run the workspace indexer:
   ```bash
   node workspace-index.js
   ```

3. Open the generated `WORKSPACE.md` file to view the repository structure.

## Features

- Creates a hierarchical view of all files and directories
- Generates direct links to files
- Ignores common directories like `.git` and `node_modules`
- Creates both human-readable (Markdown) and machine-readable (JSON) indexes

## Customization

You can modify the `workspace-index.js` file to:
- Change which directories and files are ignored
- Adjust the format of the output
- Add additional information to the index
