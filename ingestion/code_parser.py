import ast
from typing import List, Dict


def parse_python_file(file_record: Dict) -> Dict:
    """
    Takes a file record and extracts code structure from it.
    Works only on Python files. Others are returned as-is.
    """
    if file_record["extension"] != ".py":
        file_record["functions"] = []
        file_record["classes"] = []
        file_record["imports"] = []
        return file_record

    source_code = file_record["content"]

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        file_record["functions"] = []
        file_record["classes"] = []
        file_record["imports"] = []
        return file_record

    file_record["functions"] = extract_functions(tree, source_code)
    file_record["classes"] = extract_classes(tree)
    file_record["imports"] = extract_imports(tree)

    return file_record


def extract_functions(tree, source_code: str) -> List[Dict]:
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "docstring": ast.get_docstring(node) or "",
                "args": [arg.arg for arg in node.args.args],
            })
    return functions


def extract_classes(tree) -> List[Dict]:
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line_start": node.lineno,
                "docstring": ast.get_docstring(node) or "",
                "methods": [
                    n.name for n in ast.walk(node)
                    if isinstance(n, ast.FunctionDef)
                ],
            })
    return classes


def extract_imports(tree) -> List[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    return imports


def parse_all_files(file_records: List[Dict]) -> List[Dict]:
    parsed = []
    for record in file_records:
        parsed.append(parse_python_file(record))
    return parsed


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository

    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)

    # Show sample
    python_files = [r for r in parsed if r["extension"] == ".py"]
    sample = python_files[0]

    print(f"\nFile: {sample['relative_path']}")
    print(f"Functions found: {len(sample['functions'])}")
    print(f"Classes found  : {len(sample['classes'])}")
    print(f"Imports found  : {len(sample['imports'])}")

    if sample["functions"]:
        f = sample["functions"][0]
        print(f"\nFirst Function : {f['name']}")
        print(f"Arguments      : {f['args']}")
        print(f"Docstring      : {f['docstring'][:100] if f['docstring'] else 'None'}")