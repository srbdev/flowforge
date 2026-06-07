# FlowForge

## Development Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run the following commands:

   ```sh
   git clone https://github.com/srbdev/flowforge.git
   cd flowforge
   uv sync

   # If `~/.local/bin` isn't in your PATH, run:
   # uv tool update-shell
   uv tool install --editable .
   ```
3. Run the CLI tool with the `ff` command
