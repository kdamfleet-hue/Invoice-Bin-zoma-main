from pathlib import Path
import ast

revisions = {}
for path in Path("migrations/versions").glob("*.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"revision", "down_revision"}:
                values[name] = ast.literal_eval(node.value)
    revision = values.get("revision")
    if revision:
        parent = values.get("down_revision")
        parents = list(parent) if isinstance(parent, tuple) else ([parent] if parent else [])
        revisions[revision] = (path.name, parents)

referenced = {parent for _, parents in revisions.values() for parent in parents if parent}
heads = sorted(set(revisions) - referenced)
print("revisions", len(revisions))
print("heads", heads)
if len(heads) != 1:
    raise SystemExit("migration graph must have exactly one head")
print(f"OK: single merge head {heads[0]}")
