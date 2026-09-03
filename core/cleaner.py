import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


def _remove_readonly(func, path, excinfo):
    """Clear the readonly bit and reattempt removal on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def delete_path(target: Path, logger):
    """Safely delete a file or directory."""
    if not target.exists():
        return False
    try:
        if target.is_dir():
            shutil.rmtree(target, onerror=_remove_readonly)
        else:
            try:
                os.chmod(target, stat.S_IWRITE)
            except Exception:
                pass
            target.unlink(missing_ok=True)
        logger.info(f"Deleted: {target}")
        return True
    except Exception as e:
        logger.warning(f"Failed to remove {target}: {e}")
        return False


def clean_cpp_and_native_cache(project_dir: Path, logger):
    """Delete CMake and native build caches."""
    logger.info("=" * 60)
    logger.info("STEP 2: Deleting CMake and native build caches...")
    logger.info("=" * 60)

    android_dir = project_dir / "android"

    cache_paths = [
        android_dir / ".cxx",
        android_dir / "app" / ".cxx",
        android_dir / "build",
        android_dir / "app" / "build",
        android_dir / ".gradle",
        project_dir / "node_modules" / "expo" / "node_modules" / "expo-modules-core" / "android" / ".cxx",
        project_dir / "node_modules" / "expo-modules-core" / "android" / ".cxx",
        project_dir / "node_modules" / "react-native-worklets" / "android" / "build",
        project_dir / "node_modules" / "react-native-worklets-core" / "android" / "build",
    ]

    # Also search for any additional .cxx directories inside node_modules
    node_modules_dir = project_dir / "node_modules"
    if node_modules_dir.exists():
        try:
            for cxx_path in node_modules_dir.glob("**/android/.cxx"):
                if cxx_path not in cache_paths:
                    cache_paths.append(cxx_path)
        except Exception:
            pass

    deleted_count = 0
    for path in cache_paths:
        if path.exists():
            if delete_path(path, logger):
                deleted_count += 1

    logger.info(f"C++ / CMake cache cleanup completed. ({deleted_count} cache directories removed)")


def check_worklets_and_modules(project_dir: Path, logger, process_callback=None):
    """Check Worklets headers and installed module versions."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 3: Checking Worklets & Reanimated installation...")
    logger.info("=" * 60)

    worklets_prefab = (
        project_dir
        / "node_modules"
        / "react-native-worklets"
        / "android"
        / "build"
        / "prefab-headers"
        / "worklets"
    )
    worklets_core_prefab = (
        project_dir
        / "node_modules"
        / "react-native-worklets-core"
        / "android"
        / "build"
        / "prefab-headers"
        / "worklets"
    )

    exists = worklets_prefab.exists() or worklets_core_prefab.exists()
    logger.info(f"Test-Path prefab-headers ({worklets_prefab}): {exists}")
    if not exists:
        logger.info("Note: prefab-headers will be regenerated during next native build.")

    npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"

    for pkg in ["react-native-worklets", "react-native-reanimated"]:
        logger.info(f"\nChecking installed version for {pkg} ('npm ls {pkg}'):")
        try:
            cmd = [npm_cmd, "ls", pkg]
            process = subprocess.Popen(
                cmd,
                cwd=str(project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=sys.platform.startswith("win")
            )
            if process_callback:
                process_callback(process)

            for line in iter(process.stdout.readline, ""):
                if line:
                    logger.info("  " + line.strip())
            process.stdout.close()
            process.wait()
        except Exception as e:
            logger.warning(f"Could not check version for {pkg}: {e}")


def clean_reinstall_node_modules(project_dir: Path, logger, process_callback=None):
    """Clean reinstall node_modules and verify npm cache."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 4: Reinstalling node_modules...")
    logger.info("=" * 60)

    node_modules = project_dir / "node_modules"
    pkg_lock = project_dir / "package-lock.json"

    delete_path(node_modules, logger)
    delete_path(pkg_lock, logger)

    npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"

    # npm cache verify
    logger.info("Running: npm cache verify")
    try:
        p = subprocess.Popen(
            [npm_cmd, "cache", "verify"],
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=sys.platform.startswith("win")
        )
        if process_callback:
            process_callback(p)
        for line in iter(p.stdout.readline, ""):
            if line:
                logger.info(line.strip())
        p.stdout.close()
        p.wait()
    except Exception as e:
        logger.warning(f"npm cache verify error: {e}")

    # npm install
    logger.info("Running: npm install")
    p = subprocess.Popen(
        [npm_cmd, "install"],
        cwd=str(project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=sys.platform.startswith("win")
    )
    if process_callback:
        process_callback(p)
    for line in iter(p.stdout.readline, ""):
        if line:
            logger.info(line.strip())
    p.stdout.close()
    rc = p.wait()
    if rc != 0:
        raise Exception(f"npm install failed with exit code {rc}")
    logger.info("npm install completed successfully.")


def run_cache_clean_task(project_dir: Path, reinstall_modules: bool, logger, process_callback=None):
    """Run full C++ cache cleanup and diagnostics routine."""
    clean_cpp_and_native_cache(project_dir, logger)
    check_worklets_and_modules(project_dir, logger, process_callback)
    if reinstall_modules:
        clean_reinstall_node_modules(project_dir, logger, process_callback)

    logger.info("")
    logger.info("=" * 60)
    logger.info("C++ CACHE CLEAN & DIAGNOSTICS COMPLETE")
    logger.info("=" * 60)
