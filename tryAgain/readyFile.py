import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

class FileRearrangerLogic:
    def __init__(self):
        self.file_list = []
        self.original_folder = ""

    def add_folder(self, folder_path):
        try:
            self.file_list = [self.remove_numbering(os.path.join(folder_path, f)) for f in os.listdir(folder_path)]
            self.original_folder = folder_path
            return self.file_list, self.original_folder
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add folder: {e}")
            return [], ""

    def export_files_to_another_folder(self, export_folder):
        try:
            for index, file_path in enumerate(self.file_list):
                filename = f"{index + 1}. {os.path.basename(file_path)}"
                dest_path = os.path.join(export_folder, filename)
                dest_path = os.path.normpath(dest_path)
                shutil.copy(file_path, dest_path)
            messagebox.showinfo("Export Complete", "Files have been exported to another folder successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export files: {e}")

    def export_files_to_original_folder(self):
        if hasattr(self, 'original_folder'):
            try:
                for index, file_path in enumerate(self.file_list):
                    filename = f"{index + 1}. {os.path.basename(file_path)}"
                    dest_path = os.path.join(self.original_folder, filename)

                    file_path = os.path.normpath(file_path)
                    dest_path = os.path.normpath(dest_path)

                    if os.path.exists(dest_path):
                        os.remove(dest_path)

                    shutil.copy2(file_path, dest_path)

                new_files = {os.path.normpath(os.path.join(self.original_folder, f"{index + 1}. {os.path.basename(file_path)}"))
                             for index, file_path in enumerate(self.file_list)}

                for old_file in os.listdir(self.original_folder):
                    old_file_path = os.path.normpath(os.path.join(self.original_folder, old_file))
                    if old_file_path not in new_files:
                        os.remove(old_file_path)

                messagebox.showinfo("Export Complete", "Files have been exported to the original folder successfully.")
                return self.file_list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export files: {e}")
                return []
        else:
            messagebox.showerror("Error", "Original folder path not found.")
            return []

    def remove_numbering(self, file_path):
        filename = os.path.basename(file_path)
        new_filename = re.sub(r'^\d+\.\s*', '', filename)
        new_path = os.path.join(os.path.dirname(file_path), new_filename)

        if file_path != new_path:
            os.rename(file_path, new_path)

        return new_path

class FileRearrangerApp:
    def __init__(self, root):
        self.root = root
        self.logic = FileRearrangerLogic()

        self.root.title("File Rearranger")
        self.root.geometry("800x600")

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.map("TButton",
                  background=[('active', '#0052cc'), ('!disabled', '#0052cc')],
                  foreground=[('active', 'white'), ('!disabled', 'white')])

        style.configure("TMenubutton", padding=6, relief="flat", background="#ccc")
        style.map("TMenubutton",
                  background=[('active', '#0052cc'), ('!disabled', '#0052cc')],
                  foreground=[('active', 'white'), ('!disabled', 'white')])

        style.configure("TListbox", padding=6, relief="flat", background="#fff")
        style.map("TListbox",
                  background=[('active', '#e6f0ff'), ('!disabled', '#e6f0ff')],
                  foreground=[('active', 'black'), ('!disabled', 'black')])

        self.drag_data = {"item": None, "index": None, "label": None, "highlight": None}

        self.label_offset_x = 0
        self.label_offset_y = -100

        self.button_padx = 5
        self.button_pady = 10

        main_frame = ttk.Frame(root)
        main_frame.pack(side=tk.TOP, fill=tk.X, pady=self.button_pady)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.LEFT, padx=self.button_padx)

        self.add_button = ttk.Button(button_frame, text="Add", command=self.add_folder)
        self.add_button.pack(side=tk.LEFT, padx=self.button_padx)

        self.export_button = ttk.Menubutton(button_frame, text="Export")
        self.export_menu = tk.Menu(self.export_button, tearoff=0)
        self.export_button.config(menu=self.export_menu)
        self.export_button.pack(side=tk.LEFT, padx=self.button_padx)

        self.export_menu.add_command(label="Export to Another Folder", command=self.export_files_to_another_folder)
        self.export_menu.add_command(label="Export to Original Folder", command=self.export_files_to_original_folder)

        move_button_frame = ttk.Frame(main_frame)
        move_button_frame.pack(side=tk.RIGHT, padx=self.button_padx)

        self.move_up_button = ttk.Button(move_button_frame, text="Move Up", command=self.move_up)
        self.move_up_button.pack(side=tk.TOP, padx=self.button_padx, pady=2)

        self.move_down_button = ttk.Button(move_button_frame, text="Move Down", command=self.move_down)
        self.move_down_button.pack(side=tk.TOP, padx=self.button_padx, pady=2)

        self.folder_path_label = ttk.Label(root, text="No folder selected", foreground="blue")
        self.folder_path_label.pack(fill=tk.X, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_display = tk.Listbox(root, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)
        self.file_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, ipady=10)
        self.file_display.drop_target_register(DND_FILES)
        self.file_display.dnd_bind('<<Drop>>', self.on_drop)

        scrollbar.config(command=self.file_display.yview)

        self.file_display.bind('<Button-1>', self.start_drag)
        self.file_display.bind('<B1-Motion>', self.do_drag)
        self.file_display.bind('<ButtonRelease-1>', self.stop_drag)

    def add_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_list, self.original_folder = self.logic.add_folder(folder_path)
            self.update_display()
            self.folder_path_label.config(text=f"Current folder: {folder_path}")

    def export_files_to_another_folder(self):
        export_folder = filedialog.askdirectory()
        if export_folder:
            self.logic.export_files_to_another_folder(export_folder)

    def export_files_to_original_folder(self):
        self.file_list = self.logic.export_files_to_original_folder()
        self.update_display()

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if os.path.isfile(file):
                self.file_list.append(self.logic.remove_numbering(file))
        self.update_display()

    def start_drag(self, event):
        widget = event.widget
        listbox_index = widget.nearest(event.y)
        file_list_index = listbox_index // 2
        if file_list_index >= 0 and file_list_index < len(self.file_list):
            self.file_display.selection_clear(0, tk.END)
            self.file_display.selection_set(listbox_index)
            self.drag_data["item"] = self.file_list[file_list_index]
            self.drag_data["index"] = file_list_index
            self.drag_data["label"] = ttk.Label(widget, text=f"{file_list_index + 1}. {os.path.basename(self.file_list[file_list_index])}", relief='solid')
            self.drag_data["label"].place(x=event.x_root - widget.winfo_rootx() + self.label_offset_x, y=event.y_root - widget.winfo_rooty() + self.label_offset_y)

    def do_drag(self, event):
        if self.drag_data["item"]:
            self.drag_data["label"].place(x=event.x_root - self.root.winfo_rootx() + self.label_offset_x, y=event.y_root - self.root.winfo_rooty() + self.label_offset_y)
            widget = event.widget
            listbox_index = widget.nearest(event.y)
            file_list_index = listbox_index // 2
            if self.drag_data["highlight"] is not None:
                self.file_display.itemconfig(self.drag_data["highlight"], {'bg': 'white'})
            if file_list_index >= 0 and file_list_index < len(self.file_list):
                self.file_display.itemconfig(listbox_index, {'bg': 'lightblue'})
                self.drag_data["highlight"] = listbox_index

    def stop_drag(self, event):
        if self.drag_data["item"]:
            widget = event.widget
            listbox_index = widget.nearest(event.y)
            new_file_list_index = listbox_index // 2
            if new_file_list_index >= 0 and new_file_list_index < len(self.file_list):
                if new_file_list_index != self.drag_data["index"]:
                    self.file_list.insert(new_file_list_index, self.file_list.pop(self.drag_data["index"]))
                    self.update_display()
            self.drag_data["label"].destroy()
            if self.drag_data["highlight"] is not None:
                self.file_display.itemconfig(self.drag_data["highlight"], {'bg': 'white'})
            self.drag_data = {"item": None, "index": None, "label": None, "highlight": None}

    def move_up(self):
        selection = self.file_display.curselection()
        if selection:
            listbox_index = selection[0]
            file_list_index = listbox_index // 2
            if file_list_index > 0:
                self.file_list.insert(file_list_index - 1, self.file_list.pop(file_list_index))
                self.update_display()
                self.file_display.selection_set((file_list_index - 1) * 2)

    def move_down(self):
        selection = self.file_display.curselection()
        if selection:
            listbox_index = selection[0]
            file_list_index = listbox_index // 2
            if file_list_index < len(self.file_list) - 1:
                self.file_list.insert(file_list_index + 1, self.file_list.pop(file_list_index))
                self.update_display()
                self.file_display.selection_set((file_list_index + 1) * 2)

    def update_display(self):
        self.file_display.delete(0, tk.END)
        for index, file_path in enumerate(self.file_list):
            filename = os.path.basename(file_path)
            self.file_display.insert(tk.END, f"{index + 1}. {filename}")
            self.file_display.insert(tk.END, "")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileRearrangerApp(root)
    root.mainloop()
