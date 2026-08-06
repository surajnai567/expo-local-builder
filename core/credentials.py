import json
import shutil
from pathlib import Path

def load_credentials(project_path: Path, credentials_file: Path):
    if not credentials_file.exists():
        raise Exception("Credentials file not found.")

    try:
        with open(credentials_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "android" not in data or "keystore" not in data["android"]:
            raise Exception("Invalid credentials.json format. Missing android/keystore.")

        ks = data["android"]["keystore"]
        
        keystore_path = ks.get("keystorePath")
        if not keystore_path:
            raise Exception("keystorePath missing in credentials.json")

        full_keystore_path = project_path / keystore_path
        if not full_keystore_path.exists():
            raise Exception(f"Keystore file does not exist at {full_keystore_path}")

        return {
            "keystore_path": full_keystore_path,
            "keystore_name": Path(keystore_path).name,
            "store_password": ks.get("keystorePassword", ""),
            "key_alias": ks.get("keyAlias", ""),
            "key_password": ks.get("keyPassword", ""),
        }
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in credentials.json: {e}")

def copy_keystore(credentials, app_dir: Path):
    source = credentials["keystore_path"]
    destination = app_dir / credentials["keystore_name"]
    
    if not source.exists():
        raise Exception(f"Source keystore missing: {source}")

    shutil.copy2(source, destination)
    
    if not destination.exists():
        raise Exception(f"Failed to copy keystore to {destination}")
