import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in [ROOT / 'app.py', *sorted((ROOT / 'routes').glob('*.py'))]:
    tree = ast.parse(path.read_text(encoding='utf-8', errors='ignore'))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        routes = []
        decorators = []
        for dec in node.decorator_list:
            text = ast.get_source_segment(path.read_text(encoding='utf-8', errors='ignore'), dec) or ''
            decorators.append(text.replace('\n', ' '))
            if '.route(' in text or text.startswith('@route('):
                routes.append(text.replace('\n', ' '))
        if routes:
            auth = any(x.startswith('@login_required') or x.startswith('@role_required') or 'login_required' in x or 'role_required' in x for x in decorators)
            print(f"{path.relative_to(ROOT)}:{node.lineno}\tprotected={auth}\tfunction={node.name}\troute={' | '.join(routes)}\tdecorators={' | '.join(decorators)}")
