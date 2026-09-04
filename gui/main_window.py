import os
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
import subprocess

from utils.config import load_settings, save_settings
from utils.logger import setup_logger
from gui.components import LabeledEntry
from core.validator import validate_project
from core.credentials import load_credentials, copy_keystore
from core.gradle import update_gradle_properties, update_build_gradle
from core.builder import run_build, run_prebuild
from core.expo import load_app_json_versions, update_app_json_versions
from core.cleaner import run_cache_clean_task

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Android Builder Assistant")
        self.geometry("900x700")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.settings = load_settings()
        self.build_thread = None
        self.logger = setup_logger(self.append_log)
        self.output_folder = None
        
        self.setup_ui()
        self.load_initial_settings()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Project Selection
        self.project_frame = ctk.CTkFrame(self)
        self.project_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.project_frame.grid_columnconfigure(0, weight=1)
        
        self.project_path = LabeledEntry(self.project_frame, "Project Path:")
        self.project_path.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(self.project_frame, text="Browse", command=self.browse_project)
        self.browse_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.credentials_path = LabeledEntry(self.project_frame, "Credentials Path:")
        self.credentials_path.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.browse_cred_btn = ctk.CTkButton(self.project_frame, text="Browse", command=self.browse_credentials)
        self.browse_cred_btn.grid(row=1, column=1, padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self.project_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        
        # Build Configuration
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_columnconfigure(1, weight=1)
        self.config_frame.grid_columnconfigure(2, weight=1)
        
        # Build Type Radio
        self.build_type_var = ctk.StringVar(value="aab")
        self.type_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.type_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        ctk.CTkLabel(self.type_frame, text="Build Type:").pack(anchor="w")
        ctk.CTkRadioButton(self.type_frame, text="APK", variable=self.build_type_var, value="apk").pack(anchor="w", pady=5)
        ctk.CTkRadioButton(self.type_frame, text="AAB", variable=self.build_type_var, value="aab").pack(anchor="w", pady=5)
        
        # Options
        self.options_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.options_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        ctk.CTkLabel(self.options_frame, text="Options:").pack(anchor="w")
        self.clean_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.options_frame, text="Clean Gradle before build", variable=self.clean_var).pack(anchor="w", pady=5)
        
        self.cache_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Remove CMake cache", variable=self.cache_var).pack(anchor="w", pady=5)
        
        self.reinstall_modules_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Reinstall node_modules on clean", variable=self.reinstall_modules_var).pack(anchor="w", pady=5)
        
        # Versioning
        self.version_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.version_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nw")
        
        ctk.CTkLabel(self.version_frame, text="Versioning (Optional):").pack(anchor="w")
        
        self.version_code_var = ctk.StringVar(value="")
        self.version_code_entry = ctk.CTkEntry(self.version_frame, placeholder_text="Version Code (e.g. 2)", textvariable=self.version_code_var)
        self.version_code_entry.pack(anchor="w", pady=5)
        
        self.version_name_var = ctk.StringVar(value="")
        self.version_name_entry = ctk.CTkEntry(self.version_frame, placeholder_text="Version Name (e.g. 1.0.1)", textvariable=self.version_name_var)
        self.version_name_entry.pack(anchor="w", pady=5)
        
        # Actions
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.clean_cache_btn = ctk.CTkButton(self.action_frame, text="CLEAN C++ CACHE", fg_color="#D97706", hover_color="#B45309", command=self.start_clean_cache)
        self.clean_cache_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.prebuild_btn = ctk.CTkButton(self.action_frame, text="RUN PREBUILD", fg_color="blue", command=self.start_prebuild)
        self.prebuild_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.start_btn = ctk.CTkButton(self.action_frame, text="START BUILD", fg_color="green", command=self.start_build)
        self.start_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        self.cancel_btn = ctk.CTkButton(self.action_frame, text="CANCEL", fg_color="red", state="disabled", command=self.cancel_build)
        self.cancel_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Build Logs
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.log_frame, text="BUILD LOGS").grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
        
        self.log_textbox = ctk.CTkTextbox(self.log_frame, state="disabled", wrap="word")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Result
        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Build Status: -")
        self.result_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.open_folder_btn = ctk.CTkButton(self.result_frame, text="Open Output Folder", state="disabled", command=self.open_output_folder)
        self.open_folder_btn.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
    def load_initial_settings(self):
        self.project_path.set(self.settings.get("last_project", ""))
        self.credentials_path.set(self.settings.get("last_credentials", ""))
        self.build_type_var.set(self.settings.get("last_build_type", "aab"))
        self.clean_var.set(self.settings.get("clean_before_build", True))
        self.cache_var.set(self.settings.get("remove_cmake_cache", False))
        self.reinstall_modules_var.set(self.settings.get("reinstall_modules_on_clean", False))
        self.version_code_var.set(self.settings.get("last_version_code", ""))
        self.version_name_var.set(self.settings.get("last_version_name", ""))
        
        self.validate_paths()
        
    def save_current_settings(self):
        self.settings["last_project"] = self.project_path.get()
        self.settings["last_credentials"] = self.credentials_path.get()
        self.settings["last_build_type"] = self.build_type_var.get()
        self.settings["clean_before_build"] = self.clean_var.get()
        self.settings["remove_cmake_cache"] = self.cache_var.get()
        self.settings["reinstall_modules_on_clean"] = self.reinstall_modules_var.get()
        self.settings["last_version_code"] = self.version_code_var.get()
        self.settings["last_version_name"] = self.version_name_var.get()
        save_settings(self.settings)

    def browse_project(self):
        folder_path = filedialog.askdirectory(title="Select Expo Project Directory")
        if folder_path:
            self.project_path.set(folder_path)
            self.validate_paths()
            self.save_current_settings()

    def browse_credentials(self):
        file_path = filedialog.askopenfilename(title="Select Credentials JSON", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            self.credentials_path.set(file_path)
            self.validate_paths()
            self.save_current_settings()

    def validate_paths(self):
        project_dir = self.project_path.get()
        credentials_file = self.credentials_path.get()
        
        if not project_dir:
            self.status_label.configure(text="Status: Waiting for project", text_color="gray")
            return
            
        try:
            path_obj = Path(project_dir)
            validate_project(path_obj)
            
            vc, vn = load_app_json_versions(path_obj)
            if vc:
                self.version_code_var.set(vc)
            if vn:
                self.version_name_var.set(vn)
            
            if not credentials_file:
                self.status_label.configure(text="Status: Valid Project, waiting for credentials", text_color="orange")
                return
                
            load_credentials(Path(project_dir), Path(credentials_file))
            self.status_label.configure(text="Status: Valid Project & Credentials", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Status: {e}", text_color="red")

    def append_log(self, msg):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_build(self):
        project_dir = self.project_path.get()
        if not project_dir:
            self.append_log("ERROR: Please select a project directory.")
            return
            
        path = Path(project_dir)
        try:
            validate_project(path)
        except Exception as e:
            self.append_log(f"ERROR: {e}")
            return
            
        self.save_current_settings()
        
        self.start_btn.configure(state="disabled")
        self.prebuild_btn.configure(state="disabled")
        self.clean_cache_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.result_label.configure(text="Build Status: IN PROGRESS", text_color="yellow")
        self.open_folder_btn.configure(state="disabled")
        
        self.build_thread = threading.Thread(target=self.build_process, args=(path,), daemon=True)
        self.build_thread.start()

    def set_current_process(self, process):
        self.current_process = process

    def cancel_build(self):
        if hasattr(self, 'current_process') and self.current_process:
            self.logger.info("Attempting to cancel build...")
            self.cancel_btn.configure(state="disabled")
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    self.current_process.kill()
            except Exception as e:
                self.logger.error(f"Failed to cancel process: {e}")

    def build_process(self, path: Path):
        try:
            self.logger.info("Starting build process...")
            
            # Credentials phase
            credentials_file = Path(self.credentials_path.get())
            credentials = load_credentials(path, credentials_file)
            android_dir = path / "android"
            app_dir = android_dir / "app"
            gradle_properties = android_dir / "gradle.properties"
            build_gradle = app_dir / "build.gradle"
            
            copy_keystore(credentials, app_dir)
            update_gradle_properties(credentials, gradle_properties)
            update_build_gradle(credentials, build_gradle)
            
            v_code = self.version_code_var.get().strip()
            v_name = self.version_name_var.get().strip()
            update_app_json_versions(path, v_code, v_name)
            
            # Build phase
            build_type = self.build_type_var.get()
            clean = self.clean_var.get()
            cache = self.cache_var.get()
            
            output_dir = run_build(android_dir, build_type, clean, cache, self.logger, self.set_current_process)
            self.output_folder = output_dir
            
            self.after(0, self.build_success)
        except Exception as e:
            self.logger.error(str(e))
            self.after(0, self.build_failed)
            
    def build_success(self):
        self.result_label.configure(text="Build Status: SUCCESS", text_color="green")
        self.start_btn.configure(state="normal")
        self.prebuild_btn.configure(state="normal")
        self.clean_cache_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.current_process = None
        if self.output_folder and self.output_folder.exists():
            self.open_folder_btn.configure(state="normal")

    def build_failed(self):
        self.result_label.configure(text="Build Status: FAILED", text_color="red")
        self.start_btn.configure(state="normal")
        self.clean_cache_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.current_process = None
        if hasattr(self, 'prebuild_btn'):
            self.prebuild_btn.configure(state="normal")

    def start_prebuild(self):
        project_dir = self.project_path.get()
        if not project_dir:
            self.append_log("ERROR: Please select a project directory.")
            return
            
        path = Path(project_dir)
        self.start_btn.configure(state="disabled")
        self.prebuild_btn.configure(state="disabled")
        self.clean_cache_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.result_label.configure(text="Prebuild Status: IN PROGRESS", text_color="yellow")
        
        self.build_thread = threading.Thread(target=self.prebuild_process, args=(path,), daemon=True)
        self.build_thread.start()

    def prebuild_process(self, path: Path):
        try:
            self.logger.info("Starting prebuild process...")
            v_code = self.version_code_var.get().strip()
            v_name = self.version_name_var.get().strip()
            update_app_json_versions(path, v_code, v_name)
            
            run_prebuild(path, self.logger, self.set_current_process)
            self.after(0, self.prebuild_success)
        except Exception as e:
            self.logger.error(str(e))
            self.after(0, self.build_failed)

    def prebuild_success(self):
        self.result_label.configure(text="Prebuild Status: SUCCESS", text_color="green")
        self.start_btn.configure(state="normal")
        self.prebuild_btn.configure(state="normal")
        self.clean_cache_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.current_process = None

    def start_clean_cache(self):
        project_dir = self.project_path.get()
        if not project_dir:
            self.append_log("ERROR: Please select a project directory.")
            return
            
        path = Path(project_dir)
        self.save_current_settings()
        
        self.start_btn.configure(state="disabled")
        self.prebuild_btn.configure(state="disabled")
        self.clean_cache_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.result_label.configure(text="Cache Clean: IN PROGRESS", text_color="yellow")
        self.open_folder_btn.configure(state="disabled")
        
        self.build_thread = threading.Thread(target=self.clean_cache_process, args=(path,), daemon=True)
        self.build_thread.start()

    def clean_cache_process(self, path: Path):
        try:
            reinstall = self.reinstall_modules_var.get()
            run_cache_clean_task(path, reinstall, self.logger, self.set_current_process)
            self.after(0, self.clean_cache_success)
        except Exception as e:
            self.logger.error(str(e))
            self.after(0, self.clean_cache_failed)

    def clean_cache_success(self):
        self.result_label.configure(text="Cache Clean: SUCCESS", text_color="green")
        self.start_btn.configure(state="normal")
        self.prebuild_btn.configure(state="normal")
        self.clean_cache_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.current_process = None

    def clean_cache_failed(self):
        self.result_label.configure(text="Cache Clean: FAILED", text_color="red")
        self.start_btn.configure(state="normal")
        self.prebuild_btn.configure(state="normal")
        self.clean_cache_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.current_process = None

    def open_output_folder(self):
        if self.output_folder and self.output_folder.exists():
            if os.name == 'nt':
                os.startfile(self.output_folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', self.output_folder])
            else:
                subprocess.Popen(['xdg-open', self.output_folder])
