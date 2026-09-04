from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def route_has_admin_guard(path: Path, function_name: str) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            decorators = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    decorators.append((dec.func.id, [ast.literal_eval(a) for a in dec.args]))
            return ("role_required", ["admin"]) in decorators
    return False


def main() -> None:
    app = ROOT / "app.py"
    fleet = ROOT / "routes" / "fleet.py"
    assert route_has_admin_guard(app, "employees"), "employees route lacks admin guard"
    assert route_has_admin_guard(app, "employees_data"), "employees API lacks admin guard"
    assert route_has_admin_guard(fleet, "master_editor"), "master_editor route lacks admin guard"
    assert route_has_admin_guard(fleet, "api_master_data"), "master_data API lacks admin guard"

    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    index = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert base.count("{% if is_admin %}") >= 2, "admin-only navigation guards missing"
    assert "{% if is_admin %}" in index and "/employees" in index, "employee shortcut is not guarded"
    assert '"is_admin": session.get("role") == "admin"' in app.read_text(encoding="utf-8"), "is_admin context missing"
    print("admin visibility checks: PASS")


if __name__ == "__main__":
    main()
