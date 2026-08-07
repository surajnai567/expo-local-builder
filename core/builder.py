import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, cwd: Path, logger, process_callback=None):
    logger.info(f"Running: {' '.join(command)}")
    
    # We use subprocess.Popen to stream the output
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    if process_callback:
        process_callback(process)
    
    for line in iter(process.stdout.readline, ""):
        if line:
            logger.info(line.strip())
            
    process.stdout.close()
    return_code = process.wait()
    
    if return_code != 0:
        raise Exception(f"Command failed with exit code {return_code}\nCommand: {' '.join(command)}")

def clean_cache(android_dir: Path, logger):
    logger.info("Removing CMake and Gradle caches...")
    paths_to_remove = [
        android_dir / ".cxx",
        android_dir / "build",
        android_dir / ".gradle"
    ]
    
    for path in paths_to_remove:
        if path.exists() and path.is_dir():
            try:
                shutil.rmtree(path)
                logger.info(f"Removed cache directory: {path}")
            except Exception as e:
                logger.warning(f"Failed to remove cache {path}: {e}")

def run_prebuild(project_dir: Path, logger, process_callback=None):
    logger.info("Running Expo prebuild...")
    command = ["npx.cmd", "expo", "prebuild", "--no-install", "--clean", "--platform", "android"] if sys.platform.startswith("win") else ["npx", "expo", "prebuild", "--no-install", "--clean", "--platform", "android"]
    run_command(command, project_dir, logger, process_callback)

def run_build(android_dir: Path, build_type: str, clean_before: bool, remove_cache: bool, logger, process_callback=None):
    gradlew = str(android_dir / "gradlew.bat") if sys.platform.startswith("win") else "./gradlew"
    
    if remove_cache:
        clean_cache(android_dir, logger)

    if clean_before:
        logger.info("Cleaning Gradle project...")
        run_command([gradlew, "clean"], android_dir, logger, process_callback)
        
    if build_type.lower() == "apk":
        task = "assembleRelease"
        output = android_dir / "app" / "build" / "outputs" / "apk" / "release"
    elif build_type.lower() == "aab":
        task = "bundleRelease"
        output = android_dir / "app" / "build" / "outputs" / "bundle" / "release"
    else:
        raise Exception("BUILD_TYPE must be either 'apk' or 'aab'.")
        
    logger.info(f"Building {build_type.upper()}...")
    run_command([gradlew, task], android_dir, logger, process_callback)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("BUILD SUCCESS")
    logger.info("=" * 60)
    logger.info("Output Folder:")
    logger.info(str(output))
    
    return output
