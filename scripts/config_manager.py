import os
import sys
import json
from pathlib import Path

DEFAULT_CONFIG_FILENAME = ".ticket_config.json"

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "image_generator": "auto",       # options: "auto", "native", "dall-e-3", "custom_api", "poster_crop"
    "output_dir": "auto",             # options: "auto" (defaults to ./output), or a custom path
    "scale": 4.0,                     # 4.0 for Retina 1536x2732, 2.8125 for 1080x1920
    "api_key": "",                    # optional API Key if using custom API
    "api_endpoint": ""                # optional custom endpoint
}

def find_config_file():
    # 1. Current working directory
    cwd_cfg = Path.cwd() / DEFAULT_CONFIG_FILENAME
    if cwd_cfg.exists():
        return cwd_cfg

    # 2. Skill directory
    skill_dir = Path(__file__).resolve().parent.parent
    skill_cfg = skill_dir / DEFAULT_CONFIG_FILENAME
    if skill_cfg.exists():
        return skill_cfg

    # 3. User home directory ~/.config/movie-ticket/config.json
    home_cfg = Path.home() / ".config" / "movie-ticket" / "config.json"
    if home_cfg.exists():
        return home_cfg

    return None

def load_config():
    cfg_path = find_config_file()
    if cfg_path and cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = dict(DEFAULT_CONFIG)
                merged.update(data)
                return merged, cfg_path
        except Exception:
            pass
    return dict(DEFAULT_CONFIG), None

def save_config(config_dict, target_path=None):
    if not target_path:
        target_path = Path.cwd() / DEFAULT_CONFIG_FILENAME
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=2)
    return target_path

def resolve_output_dir(custom_output_dir=None):
    config, _ = load_config()
    out_dir_setting = custom_output_dir or config.get("output_dir", "auto")

    if out_dir_setting != "auto" and out_dir_setting:
        p = Path(out_dir_setting)
        p.mkdir(parents=True, exist_ok=True)
        return p

    # Default to ./output in current working directory
    out_dir = Path.cwd() / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def resolve_ticket_path(filename, custom_output_dir=None):
    out_dir = resolve_output_dir(custom_output_dir)
    return out_dir / filename
