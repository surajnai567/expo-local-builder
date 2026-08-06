import customtkinter as ctk

class LabeledEntry(ctk.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.entry = ctk.CTkEntry(self)
        self.entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

    def get(self):
        return self.entry.get()

    def set(self, text):
        self.entry.delete(0, 'end')
        if text:
            self.entry.insert(0, text)
