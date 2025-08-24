from fastmcp import FastMCP
import os

mcp = FastMCP("Filesystem MCP")

@mcp.tool(
        description="List all files in a directory. Takes a keyword argument directory of type string"
)
def list_files(directory: str) -> list:
    """List all files in a directory."""
    print("list_files call entered : "+directory)
    return os.listdir(directory)

@mcp.tool(
 description="read contents of files at a give path. Takes a keyword argument path of type string"
)
def read_file(path: str) -> str:
    """Read contents of a file."""
    print("read file method call enter :"+path)
    with open(path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()

