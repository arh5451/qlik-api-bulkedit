from pathlib import Path
import yaml

def load_config():
    # config.py → config/ → project root
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)