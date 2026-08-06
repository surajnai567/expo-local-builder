from pathlib import Path

def update_gradle_properties(credentials, gradle_properties_path: Path):
    if not gradle_properties_path.exists():
        raise Exception(f"gradle.properties file missing at {gradle_properties_path}")

    with open(gradle_properties_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    keys = [
        "MYAPP_UPLOAD_STORE_FILE",
        "MYAPP_UPLOAD_STORE_PASSWORD",
        "MYAPP_UPLOAD_KEY_ALIAS",
        "MYAPP_UPLOAD_KEY_PASSWORD"
    ]
    
    new_lines = [line for line in lines if not any(line.strip().startswith(k + "=") for k in keys)]
    
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
        
    new_lines.append(f"MYAPP_UPLOAD_STORE_FILE={credentials['keystore_name']}\n")
    new_lines.append(f"MYAPP_UPLOAD_STORE_PASSWORD={credentials['store_password']}\n")
    new_lines.append(f"MYAPP_UPLOAD_KEY_ALIAS={credentials['key_alias']}\n")
    new_lines.append(f"MYAPP_UPLOAD_KEY_PASSWORD={credentials['key_password']}\n")

    with open(gradle_properties_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def update_build_gradle(credentials, build_gradle_path: Path):
    if not build_gradle_path.exists():
        raise Exception(f"build.gradle file missing at {build_gradle_path}")
        
    with open(build_gradle_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    in_signing_configs = False
    in_debug = False
    debug_brace_count = 0
    signing_configs_brace_count = 0
    
    in_build_types = False
    in_release = False
    bt_release_brace = 0
    bt_brace = 0
    
    release_added = False
    skip_existing_release = False
    release_brace_count = 0
    
    for i, line in enumerate(lines):
        # BUILD TYPES modifications
        if "buildTypes" in line and "{" in line:
            in_build_types = True
            bt_brace = 1
            new_lines.append(line)
            continue
            
        if in_build_types:
            bt_brace += line.count("{") - line.count("}")
            if bt_brace == 0:
                in_build_types = False
                
            if "release" in line and "{" in line:
                in_release = True
                bt_release_brace = 1
            elif in_release:
                bt_release_brace += line.count("{") - line.count("}")
                if bt_release_brace == 0:
                    in_release = False
                
                if "signingConfig signingConfigs.debug" in line:
                    line = line.replace("signingConfig signingConfigs.debug", "signingConfig signingConfigs.release")
        
        # SIGNING CONFIGS modifications
        if "signingConfigs" in line and "{" in line:
            in_signing_configs = True
            signing_configs_brace_count = 1
            new_lines.append(line)
            continue
            
        if in_signing_configs:
            signing_configs_brace_count += line.count("{") - line.count("}")
            if signing_configs_brace_count == 0:
                in_signing_configs = False
                
            if "release" in line and "{" in line and not in_debug:
                skip_existing_release = True
                release_brace_count = 1
                continue
                
            if skip_existing_release:
                release_brace_count += line.count("{") - line.count("}")
                if release_brace_count == 0:
                    skip_existing_release = False
                continue
                
            if "debug" in line and "{" in line and not skip_existing_release:
                in_debug = True
                debug_brace_count = 1
            elif in_debug:
                debug_brace_count += line.count("{") - line.count("}")
                if debug_brace_count == 0:
                    in_debug = False
                    new_lines.append(line)
                    if not release_added:
                        new_lines.append(f"        release {{\n")
                        new_lines.append(f"            if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE')) {{\n")
                        new_lines.append(f"                storeFile file(MYAPP_UPLOAD_STORE_FILE)\n")
                        new_lines.append(f"                storePassword MYAPP_UPLOAD_STORE_PASSWORD\n")
                        new_lines.append(f"                keyAlias MYAPP_UPLOAD_KEY_ALIAS\n")
                        new_lines.append(f"                keyPassword MYAPP_UPLOAD_KEY_PASSWORD\n")
                        new_lines.append(f"            }}\n")
                        new_lines.append(f"        }}\n")
                        release_added = True
                    continue

        new_lines.append(line)

    with open(build_gradle_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

