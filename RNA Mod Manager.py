import os
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Button, filedialog
import json

class ModManager:
    CONFIG_FILE = "mod_manager_config.json"
    VALID_EXTENSIONS = ['.pak', '.utoc', '.ucas']

    def __init__(self, master):
        self.master = master
        self.master.title("Game Mod Manager")

        self.mod_folder = self.load_config()

        self.mod_listbox = Listbox(master, selectmode=tk.SINGLE)
        self.mod_listbox.pack(fill=tk.BOTH, expand=1)

        scrollbar = Scrollbar(master, orient=tk.VERTICAL, command=self.mod_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mod_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(master)
        btn_frame.pack(fill=tk.X)

        refresh_btn = Button(btn_frame, text="Refresh List", command=self.refresh_mod_list)
        refresh_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        enable_btn = Button(btn_frame, text="Enable Mod", command=self.enable_mod)
        enable_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        disable_btn = Button(btn_frame, text="Disable Mod", command=self.disable_mod)
        disable_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        delete_btn = Button(btn_frame, text="Delete Mod", command=self.delete_mod)
        delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        change_folder_btn = Button(btn_frame, text="Change Folder", command=self.change_mod_folder)
        change_folder_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self.mods = {}
        self.refresh_mod_list()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            mod_folder = config.get("mod_folder", "")
            if mod_folder and os.path.isdir(mod_folder):
                return mod_folder

        return self.ask_for_mod_folder()

    def save_config(self):
        config = {"mod_folder": self.mod_folder}
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def ask_for_mod_folder(self):
        mod_folder = filedialog.askdirectory(title="Select Mods Folder")
        if not mod_folder:
            messagebox.showerror("Error", "You must select a mods folder.")
            self.master.destroy()
        else:
            self.mod_folder = mod_folder
            self.save_config()
            return mod_folder

    def change_mod_folder(self):
        self.mod_folder = self.ask_for_mod_folder()
        self.refresh_mod_list()

    def refresh_mod_list(self):
        self.mod_listbox.delete(0, tk.END)
        self.mods = self.get_mods()
        for mod, files in self.mods.items():
            is_disabled = any('_Disabled' in file for file in files)
            mod_text = mod + " (Disabled)" if is_disabled else mod
            self.mod_listbox.insert(tk.END, mod_text)
            text_color = "red" if is_disabled else "black"
            self.mod_listbox.itemconfig(tk.END, {'fg': text_color})

    def get_mods(self):
        print(f"Reading mods from folder: {self.mod_folder}")
        mod_files = [f for f in os.listdir(self.mod_folder) if any(f.endswith('_P' + ext) for ext in self.VALID_EXTENSIONS) or '_Disabled' in f]
        print(f"Mod files ending with '_P' and valid extensions, or with '_Disabled' in name: {mod_files}")
        mods = {}
        for file in mod_files:
            base_name, _ = os.path.splitext(file)
            actual_base_name, _ = os.path.splitext(base_name[:-9]) if '_Disabled' in base_name else os.path.splitext(base_name)
            if actual_base_name not in mods:
                mods[actual_base_name] = []
            mods[actual_base_name].append(file)
        print(f"Identified mods: {mods}")
        return mods

    def enable_mod(self):
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            mod_name = selected_mod.split(" (Disabled)")[0]
            for file in self.mods[mod_name]:
                if '_Disabled' in file:
                    new_name = file.replace('_Disabled', '')
                    os.rename(os.path.join(self.mod_folder, file), os.path.join(self.mod_folder, new_name))
            self.refresh_mod_list()

    def disable_mod(self):
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            mod_name = selected_mod.split(" (Disabled)")[0]
            for file in self.mods[mod_name]:
                if '_Disabled' not in file:
                    base_name, ext = os.path.splitext(file)
                    new_name = f"{base_name}_Disabled{ext}"
                    os.rename(os.path.join(self.mod_folder, file), os.path.join(self.mod_folder, new_name))
            self.refresh_mod_list()

    def delete_mod(self):
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            mod_name = selected_mod.split(" (Disabled)")[0]
            confirm = messagebox.askyesno("Delete Mod", f"Are you sure you want to delete the mod '{mod_name}'?")
            if confirm:
                for file in self.mods[mod_name]:
                    file_path = os.path.join(self.mod_folder, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                self.refresh_mod_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModManager(root)
    root.mainloop()
