from pathlib import Path

def validate_project(project_path: Path):
    if not project_path.exists() or not project_path.is_dir():
        raise Exception("Invalid Expo project. Folder does not exist.")

    android_dir = project_path / "android"
    if not android_dir.exists() or not android_dir.is_dir():
        raise Exception("Invalid Expo project. Android folder not found.")

    package_json = project_path / "package.json"
    if not package_json.exists():
        raise Exception("Invalid Expo project. package.json not found.")

    return True
