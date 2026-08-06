# Android Builder Assistant

A desktop GUI application to automate Android release builds for Expo / React Native applications.

## Purpose
Android Builder Assistant allows developers to select an Expo project, automatically configure Android signing, manage versions and version codes, and build APK or AAB files without manually running terminal commands.

## Features
- **Project Selection**: Automatically detects and validates Expo project directories.
- **Credentials Handling**: Configures Keystore copying and Gradle updates based on a simple `credentials.json` file.
- **Build Types**: Easy toggling between building an APK or an AAB (Android App Bundle).
- **Versioning (New)**: Reads and parses `app.json` from Expo projects. Allows you to easily bump the Version Name and Version Code directly from the UI before triggering a build.
- **Cache Management**: Provides options to clean Gradle and remove CMake caches before building.
- **Real-Time Logs**: View Gradle build output in real-time in the GUI.
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
The UI will automatically pull the current Version Code and Version Name from your project's `app.json`. You can modify these values in the UI, and they will be saved back into `app.json` upon building.

### 4. Build
Select your build type (APK or AAB), choose whether to clean the build cache, and click **Start Build**. You will be able to monitor the live logs and open the output folder once complete.

## Build executable
To create a standalone executable using PyInstaller:
```bash
pyinstaller --onefile --windowed app.py
```

## Contributing
Contributions are welcome. Currently, the architecture is split into `gui` for UI components and `core` for build logic (such as Gradle updates and Expo `app.json` parsing).
