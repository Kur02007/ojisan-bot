"""AST dependency-cycle check; imports no application code."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'src'
files={'.'.join(p.relative_to(root).with_suffix('').parts):p for p in root.rglob('*.py') if p.name!='__init__.py'}
graph={}
for name,path in files.items():
    deps=set()
    for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(n,ast.ImportFrom) and n.module:
            if n.module in files:deps.add(n.module)
            for item in n.names:
                candidate=n.module+'.'+item.name
                if candidate in files:deps.add(candidate)
        elif isinstance(n,ast.Import):
            deps.update(a.name for a in n.names if a.name in files)
    graph[name]=deps
done=set();active=set()
def visit(name,trail):
    if name in active:raise SystemExit('Import cycle: '+' -> '.join(trail+[name]))
    if name in done:return
    active.add(name)
    for dep in graph[name]:visit(dep,trail+[name])
    active.remove(name);done.add(name)
for name in graph:visit(name,[])
print(f'{len(graph)} modules parsed; no internal import cycles.')
