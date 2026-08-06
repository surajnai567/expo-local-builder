#!/usr/bin/env python3
"""
Android Release Builder

Requirements:
    Python 3.9+

Project Structure:

project/
│
├── credentials.json
├── credentials/
│   └── android/
│       └── keystore.jks
│
├── android/
│   ├── app/
│   └── gradle.properties
│
└── build_android.py
"""

import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(r"D:\lifeplanner")

# Build type: "apk" or "aab"
BUILD_TYPE = "aab"

# Clean before build
CLEAN_BUILD = True

# ============================================================


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

logger = logging.getLogger("android-builder")


class BuildError(Exception):
    """Custom build exception."""


def require_file(path: Path):
    if not path.exists():
        raise BuildError(f"Required file not found:\n{path}")

    if not path.is_file():
        raise BuildError(f"Expected file but found something else:\n{path}")


def require_directory(path: Path):
    if not path.exists():
        raise BuildError(f"Required directory not found:\n{path}")

    if not path.is_dir():
        raise BuildError(f"Expected directory but found something else:\n{path}")


def load_credentials():
    credentials_file = PROJECT_ROOT / "credentials.json"

    require_file(credentials_file)

    try:
        with open(credentials_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        ks = data["android"]["keystore"]

        return {
            "keystore_path": PROJECT_ROOT / ks["keystorePath"],
            "keystore_name": Path(ks["keystorePath"]).name,
            "store_password": ks["keystorePassword"],
            "key_alias": ks["keyAlias"],
            "key_password": ks["keyPassword"],
        }

    except KeyError as e:
        raise BuildError(f"Missing key in credentials.json: {e}")

    except json.JSONDecodeError as e:
        raise BuildError(f"Invalid JSON in credentials.json\n{e}")


def copy_keystore(credentials, app_dir: Path):
    source = credentials["keystore_path"]
    destination = app_dir / credentials["keystore_name"]

    require_file(source)

    logger.info("Copying keystore...")
    shutil.copy2(source, destination)

    logger.info("Keystore copied to %s", destination)


def update_gradle_properties(credentials, gradle_properties: Path):
    require_file(gradle_properties)

    logger.info("Updating gradle.properties...")

    props = {}

    with open(gradle_properties, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                props[key] = value

    props["MYAPP_UPLOAD_STORE_FILE"] = credentials["keystore_name"]
    props["MYAPP_UPLOAD_STORE_PASSWORD"] = credentials["store_password"]
    props["MYAPP_UPLOAD_KEY_ALIAS"] = credentials["key_alias"]
    props["MYAPP_UPLOAD_KEY_PASSWORD"] = credentials["key_password"]

    with open(gradle_properties, "w", encoding="utf-8") as f:
        for key, value in props.items():
            f.write(f"{key}={value}\n")

    logger.info("gradle.properties updated successfully.")


def run_command(command, cwd: Path):
    logger.info("Running: %s", " ".join(command))

    result = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
    )

    if result.returncode != 0:
        raise BuildError(
            f"Command failed with exit code {result.returncode}\n"
            f"Command: {' '.join(command)}"
        )


def clean(android_dir: Path):
    gradlew = "gradlew.bat" if sys.platform.startswith("win") else "./gradlew"

    logger.info("Cleaning Gradle project...")

    run_command([gradlew, "clean"], android_dir)


def build(android_dir: Path):
    gradlew = "gradlew.bat" if sys.platform.startswith("win") else "./gradlew"

    if BUILD_TYPE.lower() == "apk":
        task = "assembleRelease"
        output = (
            android_dir
            / "app"
            / "build"
            / "outputs"
            / "apk"
            / "release"
        )

    elif BUILD_TYPE.lower() == "aab":
        task = "bundleRelease"
        output = (
            android_dir
            / "app"
            / "build"
            / "outputs"
            / "bundle"
            / "release"
        )

    else:
        raise BuildError(
            "BUILD_TYPE must be either 'apk' or 'aab'."
        )

    logger.info("Building %s...", BUILD_TYPE.upper())

    run_command([gradlew, task], android_dir)

    logger.info("")
    logger.info("=" * 60)
    logger.info("BUILD SUCCESS")
    logger.info("=" * 60)
    logger.info("Output Folder:")
    logger.info(output)


def main():
    try:
        require_directory(PROJECT_ROOT)

        android_dir = PROJECT_ROOT / "android"
        app_dir = android_dir / "app"
        gradle_properties = android_dir / "gradle.properties"

        require_directory(android_dir)
        require_directory(app_dir)

        credentials = load_credentials()

        copy_keystore(credentials, app_dir)

        update_gradle_properties(credentials, gradle_properties)

        if CLEAN_BUILD:
            clean(android_dir)

        build(android_dir)

    except BuildError as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("BUILD FAILED")
        logger.error("=" * 60)
        logger.error(e)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.error("Build cancelled by user.")
        sys.exit(1)

    except Exception:
        logger.exception("Unexpected error occurred.")
        sys.exit(1)


if __name__ == "__main__":
    main()