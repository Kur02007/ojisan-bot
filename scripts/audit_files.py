"""Inspect publishable files, reporting paths and rules without secret values."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
excluded={'.git','.venv','venv','__pycache__','.pytest_cache','build','dist'}
rules={
 'private key':r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
 'Google API key':r'AIza[0-9A-Za-z_-]{35}',
 'GitHub token':r'gh[pousr]_[A-Za-z0-9]{36,}',
 'Discord token':r'[MNO][A-Za-z\d_-]{23,27}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,40}',
 'AWS key':r'AKIA[0-9A-Z]{16}',
 'IPv4 URL':r'https?://(?!(?:127\.0\.0\.1|0\.0\.0\.0)(?![\d.]))(?:\d{1,3}\.){3}\d{1,3}(?![\w.])',
}
errors=[];count=0
for p in root.rglob('*'):
    if not p.is_file() or any(part in excluded or part.endswith('.egg-info') for part in p.relative_to(root).parts):continue
    relative=p.relative_to(root).as_posix()
    if p.name.startswith('.env') and p.name!='.env.example' or p.suffix in ('.jsonl','.log','.db','.pem','.key') or p.name.startswith('celerybeat-schedule'):
        errors.append((relative,'runtime or secret file'));continue
    count+=1
    try:text=p.read_text(encoding='utf-8-sig')
    except UnicodeError:
        errors.append((relative,'unexpected binary file'));continue
    for label,pattern in rules.items():
        if re.search(pattern,text):errors.append((relative,label))
for path,rule in errors:print(path+': '+rule)
if errors:raise SystemExit(1)
print(f'{count} candidate files inspected; no configured secret-pattern matches or runtime artifacts.')
