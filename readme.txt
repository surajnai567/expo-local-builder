============================================================
ANDROID BUILDER ASSISTANT - APPLICATION SPECIFICATION
============================================================

Project Name:
Android Builder Assistant

Purpose:
A desktop GUI application to automate Android release builds
for Expo / React Native applications.

The application should allow developers to select an Expo
project, automatically configure Android signing, and build
APK/AAB files without manually running terminal commands.

Target Platform:
- Windows 10/11
- Python 3.10+

Technology:
- Python
- CustomTkinter for GUI
- Threading for background tasks
- subprocess for Gradle execution
- JSON for configuration
- pathlib for file handling


============================================================
1. CORE FEATURES
============================================================


The application must provide:

1. Project selection
2. Credentials detection
3. Keystore management
4. Gradle configuration
5. Android clean/build automation
6. Real-time build logs
7. Build status reporting
8. Output file management


============================================================
2. PROJECT STRUCTURE
============================================================


The application should follow this structure:

android-builder/

│
├── app.py
│
├── gui/
│   ├── main_window.py
│   ├── components.py
│
├── core/
│   ├── builder.py
│   ├── credentials.py
│   ├── gradle.py
│   ├── validator.py
│
├── utils/
│   ├── logger.py
│   ├── config.py
│
├── data/
│   └── settings.json
│
├── requirements.txt
│
└── README.md



============================================================
3. GUI REQUIREMENTS
============================================================


Framework:
CustomTkinter


Window:

Size:
900 x 700

Theme:
Dark mode by default


Main Layout:


------------------------------------------------------------

ANDROID BUILDER ASSISTANT

------------------------------------------------------------


PROJECT

[ Project Path Text Box                    ]

[ Browse Button ]


Status:

✓ Android folder detected

✓ credentials.json detected


------------------------------------------------------------


BUILD CONFIGURATION


Build Type:

( ) APK

( ) AAB


Options:

[x] Clean Gradle before build

[x] Remove CMake cache


------------------------------------------------------------


ACTIONS


[ START BUILD ]

[ CANCEL BUILD ]


------------------------------------------------------------


BUILD LOGS


Scrollable text area:

Example:

INFO:
Loading credentials.json

INFO:
Copying keystore

INFO:
Updating gradle.properties

INFO:
Running gradlew clean

INFO:
Building bundleRelease


------------------------------------------------------------


RESULT


Build Status:

SUCCESS / FAILED


[ Open Output Folder ]



============================================================
4. PROJECT VALIDATION
============================================================


Before starting build validate:


Project folder exists:

Required:


PROJECT_ROOT/

Must contain:


android/

package.json

credentials.json



If missing:

Show error:

"Invalid Expo project. Android folder not found"



============================================================
5. CREDENTIALS HANDLING
============================================================


Read:

credentials.json


Expected format:


{
  "android": {
    "keystore": {
      "keystorePath":
      "credentials/android/keystore.jks",

      "keystorePassword": "",

      "keyAlias": "",

      "keyPassword": ""
    }
  }
}



Validation:

Check:

- JSON is valid
- android key exists
- keystore section exists
- keystore file exists



Never create missing files.


If missing:

Show:

"Keystore file does not exist"



============================================================
6. KEYSTORE PROCESS
============================================================


Source:

credentials.json


Example:


credentials/android/keystore.jks



Destination:


android/app/


Example:


android/app/keystore.jks



Process:


1. Validate source keystore

2. Copy keystore

3. Verify copied file exists


Failure:

Stop build immediately.



============================================================
7. GRADLE.PROPERTIES UPDATE
============================================================


File:

android/gradle.properties



The application must:


- Verify file exists
- Never create it


Add/update:


MYAPP_UPLOAD_STORE_FILE=keystore.jks

MYAPP_UPLOAD_STORE_PASSWORD=password

MYAPP_UPLOAD_KEY_ALIAS=alias

MYAPP_UPLOAD_KEY_PASSWORD=password



Existing properties must remain unchanged.


============================================================
8. GRADLE BUILD PROCESS
============================================================


Detect OS:


Windows:

gradlew.bat


Linux/Mac:

./gradlew



Commands:


Clean:


gradlew clean



APK:

gradlew assembleRelease



AAB:

gradlew bundleRelease



The process must run in background thread.


The GUI must not freeze.



============================================================
9. LOGGING SYSTEM
============================================================


Use Python logging.


Log levels:


INFO

WARNING

ERROR



Logs must appear:


1. GUI log viewer

2. Local log file


Example:


logs/

build_2026_07_19_120000.log



============================================================
10. THREADING
============================================================


Gradle builds can take several minutes.


Requirements:


Never execute Gradle on main GUI thread.



Use:


threading.Thread


or


concurrent.futures



Main thread:

GUI


Worker thread:

Build process



============================================================
11. ERROR HANDLING
============================================================


Handle:


- Missing project folder
- Missing android folder
- Missing credentials.json
- Invalid JSON
- Missing keystore
- Gradle failure
- Permission errors
- User cancellation


Every error should:


1. Stop process

2. Write log

3. Show GUI message



============================================================
12. CONFIGURATION STORAGE
============================================================


Save:


data/settings.json



Store:


{
 "last_project":
 "D:/lifeplanner",

 "last_build_type":
 "aab",

 "clean_before_build":
 true
}



Load automatically on startup.



============================================================
13. BUILD OUTPUT
============================================================


APK output:


android/app/build/outputs/apk/release/


AAB output:


android/app/build/outputs/bundle/release/



After successful build:


Show:

Build completed successfully


Buttons:


Open Folder

Copy Path



============================================================
14. CACHE CLEANING
============================================================


Optional checkbox:


Remove build cache



If enabled delete:


android/.cxx

android/build

android/.gradle



Never delete:

node_modules

package files



============================================================
15. UI QUALITY
============================================================


Requirements:


- Modern dark theme
- Rounded buttons
- Proper spacing
- Responsive resizing
- Clear status indicators
- No freezing
- User-friendly errors



============================================================
16. PACKAGING
============================================================


The final application should support:


Development:


python app.py



Production:


PyInstaller


Command:


pyinstaller
--onefile
--windowed
--icon assets/icon.ico
app.py



Output:


AndroidBuilderAssistant.exe



============================================================
17. FUTURE EXTENSIONS
============================================================


Possible additions:


- Expo prebuild button
- Version code increment
- Version name editor
- Multiple project profiles
- Automatic Play Store upload
- Firebase App Distribution
- Build history
- CI/CD integration



============================================================
END OF SPECIFICATION
============================================================