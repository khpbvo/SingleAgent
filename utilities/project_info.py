import os
import re
from functools import lru_cache
from typing import Any, Dict
import toml

@lru_cache(maxsize=None)
def discover_project_info(root_dir: str) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "name": None,
        "root_dir": root_dir,
        "language": "python",
        "entry_points": [],
        "source_dirs": [],
        "test_dirs": [],
        "dependencies": {},
        "dev_dependencies": {},
        "config_files": [],
    }

    # 1) config files
    for fname in ("pyproject.toml", "setup.py", "requirements.txt", "tox.ini", "setup.cfg"):
        if os.path.exists(os.path.join(root_dir, fname)):
            info["config_files"].append(fname)

    # 2) pyproject.toml (PEP621 / Poetry)
    pyproj = os.path.join(root_dir, "pyproject.toml")
    if os.path.exists(pyproj):
        data = toml.load(pyproj)
        # project name
        info["name"] = data.get("project", {}).get("name") \
                        or data.get("tool", {}).get("poetry", {}).get("name")
        # entry‑points (poetry.scripts)
        scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
        for k, v in scripts.items():
            info["entry_points"].append(v)

    # 3) requirements.txt → dependencies
    req = os.path.join(root_dir, "requirements.txt")
    if os.path.exists(req):
        with open(req, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # simple split on == or >=
                parts = re.split(r"(?:==|>=)", line, maxsplit=1)
                pkg = parts[0]
                ver = parts[1] if len(parts) > 1 else ""
                info["dependencies"][pkg] = ver

    # 4) scan for source/ test dirs
    with os.scandir(root_dir) as it:
        for entry in it:
            if entry.is_dir():
                name = entry.name
                if name in ("src", "lib"):
                    info["source_dirs"].append(name)
                if name in ("tests", "test"):
                    info["test_dirs"].append(name)

    return info
