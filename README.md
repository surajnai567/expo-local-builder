# Android Builder Assistant

A desktop GUI application to automate Android release builds for Expo / React Native applications.

## Purpose
Android Builder Assistant allows developers to select an Expo project, automatically configure Android signing, manage versions and version codes, and build APK or AAB files without manually running terminal commands.

## Features
- **Project Selection**: Automatically detects and validates Expo project directories.
- **Credentials Handling**: Configures Keystore copying and Gradle updates based on a simple `credentials.json` file.
- **Build Types**: Easy toggling between building an APK or an AAB (Android App Bundle).
- **Versioning**: Reads and parses `app.json` from Expo projects. Allows you to easily bump the Version Name and Version Code directly from the UI before triggering a build.
- **C++ / Native Cache Cleaner**: Automatically wipes CMake `.cxx` caches, Gradle caches, Expo module caches, and Worklets build folders to resolve native C++ build errors.
- **Dependency Diagnostics**: Inspects Worklets prefab-headers and runs `npm ls` checks for `react-native-worklets` and `react-native-reanimated`.
- **Prebuild & Reinstall Options**: Run `expo prebuild` or perform a clean reinstall of `node_modules` directly from the GUI.
- **Real-Time Logs**: View Gradle and cleanup output in real-time in the GUI with process cancellation support.
- **Modern Interface**: Built with Python and `customtkinter` for a native, dark-themed experience.

## Requirements
- Windows 10/11
- Python 3.10+

## Setup & Installation
1. Clone this repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: ensure `customtkinter` and other dependencies are installed)*

## Usage
Run the application by executing:
```bash
python app.py
```
*(or run `run.bat`)*

### 1. Select a Project
Browse and select the root directory of your Expo project. The application will validate the presence of the `android/` directory and `package.json`.

### 2. Supply Credentials
Create a `credentials.json` file pointing to your keystore and supply it to the app.
Example format:
```json
{
  "android": {
    "keystore": {
      "keystorePath": "path/to/keystore.jks",
      "keystorePassword": "your_password",
      "keyAlias": "your_alias",
      "keyPassword": "your_key_password"
    }
  }
}
```

### 3. Update Versions (Optional)
The UI will automatically pull the current Version Code and Version Name from your project's `app.json`. You can modify these values in the UI, and they will be saved back into `app.json` upon building or prebuilding.

### 4. Build Configuration & Options
Configure the build behavior using the checkboxes in the **Options** panel:
- **`Clean Gradle before build`**: Executes `gradlew.bat clean` prior to compilation to remove previous Java/Kotlin bytecode and avoid incremental build issues.
- **`Remove CMake cache`**: Automatically deletes `android/.cxx`, `android/build`, and `android/.gradle` directories before building.
- **`Reinstall node_modules on clean`**: When using the **CLEAN C++ CACHE** button, also deletes `node_modules` and `package-lock.json`, runs `npm cache verify`, and executes `npm install`.

### 5. Actions & Building
- **`CLEAN C++ CACHE`**: Automatically removes all native C++ build caches (`android/.cxx`, `android/app/.cxx`, `android/build`, `android/app/build`, `expo-modules-core` `.cxx`, and `react-native-worklets` build directories) and runs Worklets / Reanimated dependency diagnostics.
- **`RUN PREBUILD`**: Executes `npx expo prebuild --no-install --clean --platform android` to regenerate the native Android directory.
- **`START BUILD`**: Signs and builds the selected format (APK or AAB) with real-time logs.
- **`CANCEL`**: Safely terminates the running build or background process.

Once the build is complete, click **Open Output Folder** to access the generated APK/AAB.

## Build Executable
To create a standalone executable using PyInstaller:
```bash
pyinstaller --onefile --windowed app.py
```

## Architecture & Contributing
Contributions are welcome. The project is organized as:
- `gui/`: User interface components and window management (`main_window.py`, `components.py`).
- `core/`: Core automation logic:
  - `cleaner.py`: C++ / CMake cache cleaning, Worklets diagnostics, and dependency management.
  - `builder.py`: Gradle build execution and Expo prebuild tasks.
  - `credentials.py`: Keystore loading and validation.
  - `gradle.py`: Gradle properties and `build.gradle` signing injection.
  - `expo.py`: `app.json` version reading and updating.
  - `validator.py`: Project path validation.
- `utils/`: Settings persistence and real-time logging utilities.
