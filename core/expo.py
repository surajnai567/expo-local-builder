import json
from pathlib import Path

def load_app_json_versions(project_dir: Path):
    app_json_path = project_dir / "app.json"
    if not app_json_path.exists():
        return "", ""
        
    try:
        with open(app_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        expo_data = data.get("expo", {})
        version = expo_data.get("version", "1.0.0")
        version_code = expo_data.get("android", {}).get("versionCode", 1)
        
        return str(version_code), str(version)
    except Exception as e:
        print(f"Failed to read app.json: {e}")
        return "", ""

def update_app_json_versions(project_dir: Path, version_code: str, version_name: str):
    app_json_path = project_dir / "app.json"
    if not app_json_path.exists():
        return
        
    try:
        with open(app_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "expo" not in data:
            data["expo"] = {}
            
        if version_name:
            data["expo"]["version"] = version_name
            
        if version_code:
            if "android" not in data["expo"]:
                data["expo"]["android"] = {}
            try:
                data["expo"]["android"]["versionCode"] = int(version_code)
            except ValueError:
                pass
                
        with open(app_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Failed to update app.json: {e}")
