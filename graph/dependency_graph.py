import ast
from typing import List, Dict
from collections import defaultdict


def build_dependency_graph(file_records: List[Dict]) -> Dict:
    """
    Builds a dependency graph from all file records.
    Returns a dict showing which files import which other files.
    """
    # Map of filename -> relative_path for quick lookup
    file_map = {}
    for record in file_records:
        name = record["relative_path"].replace("\\", "/")
        file_map[name] = record

    # Graph — key: file, value: list of files it imports
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)

    for record in file_records:
        if record["extension"] != ".py":
            continue

        source = record["relative_path"].replace("\\", "/")
        imports = extract_local_imports(record["content"], source, file_map)

        for imp in imports:
            graph[source].append(imp)
            reverse_graph[imp].append(source)

    return {
        "graph": dict(graph),           # file -> files it imports
        "reverse_graph": dict(reverse_graph),  # file -> files that import it
        "file_map": file_map
    }


def extract_local_imports(content: str, current_file: str, file_map: Dict) -> List[str]:
    """
    Extracts local project imports from a Python file.
    Ignores standard library and third party imports.
    """
    local_imports = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue

            # Convert module path to file path
            # e.g. "ingestion.repo_reader" -> "ingestion/repo_reader.py"
            module_path = node.module.replace(".", "/") + ".py"

            # Check if this file exists in our repo
            for file_path in file_map.keys():
                if file_path.endswith(module_path):
                    local_imports.append(file_path)
                    break

    return local_imports


def get_file_dependencies(filepath: str, dependency_data: Dict) -> Dict:
    """
    For a given file, returns:
    - What files it imports
    - What files import it
    """
    filepath = filepath.replace("\\", "/")
    graph = dependency_data["graph"]
    reverse_graph = dependency_data["reverse_graph"]

    return {
        "file": filepath,
        "imports": graph.get(filepath, []),
        "imported_by": reverse_graph.get(filepath, []),
    }


def get_most_connected_files(dependency_data: Dict, top_n: int = 10) -> List[Dict]:
    """
    Returns the most imported files in the codebase.
    These are usually the core/important files.
    """
    reverse_graph = dependency_data["reverse_graph"]

    scored = []
    for file, importers in reverse_graph.items():
        scored.append({
            "file": file,
            "imported_by_count": len(importers),
            "imported_by": importers
        })

    scored.sort(key=lambda x: x["imported_by_count"], reverse=True)
    return scored[:top_n]


def summarize_graph(dependency_data: Dict) -> str:
    """
    Returns a plain English summary of the dependency graph.
    Useful for showing in the chat UI.
    """
    graph = dependency_data["graph"]
    reverse_graph = dependency_data["reverse_graph"]
    most_connected = get_most_connected_files(dependency_data, top_n=5)

    summary = f"📊 Dependency Graph Summary\n"
    summary += f"{'='*40}\n"
    summary += f"Total files with imports : {len(graph)}\n"
    summary += f"Total files being imported: {len(reverse_graph)}\n\n"
    summary += f"🔑 Most Important Files (most imported):\n"

    for i, item in enumerate(most_connected):
        summary += f"  {i+1}. {item['file']} — imported by {item['imported_by_count']} files\n"

    return summary


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository
    from ingestion.code_parser import parse_all_files

    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)

    print("\n🔗 Building dependency graph...")
    dependency_data = build_dependency_graph(parsed)

    # Print summary
    print(summarize_graph(dependency_data))

    # Test specific file
    test_file = "src/flask/app.py"
    deps = get_file_dependencies(test_file, dependency_data)
    print(f"\n📄 File: {deps['file']}")
    print(f"  Imports      : {deps['imports']}")
    print(f"  Imported by  : {deps['imported_by']}")