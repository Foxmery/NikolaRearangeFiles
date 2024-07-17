# gui.py

import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from logic import FileRearrangerLogic


class FileRearrangerApp:
    def __init__(self, root):
        self.root = root
        self.logic = FileRearrangerLogic()

        self.root.title("File Rearranger")
        self.root.geometry("800x600")

        self.drag_data = {"item": None, "index": None, "label": None, "highlight": None}

        # Offset for the dragged label
        self.label_offset_x = 0
        self.label_offset_y = -100

        # Create a frame for the buttons
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.TOP, pady=10)

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_folder)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Create an Export button with a dropdown menu
        self.export_button = tk.Menubutton(button_frame, text="Export", relief=tk.RAISED)
        self.export_menu = tk.Menu(self.export_button, tearoff=0)
        self.export_button.config(menu=self.export_menu)
        self.export_button.pack(side=tk.LEFT, padx=5)

        # Add options to the export menu
        self.export_menu.add_command(label="Export to Another Folder", command=self.export_files_to_another_folder)
        self.export_menu.add_command(label="Export to Original Folder", command=self.export_files_to_original_folder)

        # Create a frame for the move buttons on the right side
        move_button_frame = tk.Frame(button_frame)
        move_button_frame.pack(side=tk.RIGHT, padx=5)

        self.move_up_button = tk.Button(move_button_frame, text="Move Up", command=self.move_up)
        self.move_up_button.pack(side=tk.LEFT, padx=5)

        self.move_down_button = tk.Button(move_button_frame, text="Move Down", command=self.move_down)
        self.move_down_button.pack(side=tk.LEFT, padx=5)

        # Create a scrollbar for the listbox
        scrollbar = tk.Scrollbar(root)
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
        file_list_index = listbox_index // 2  # Adjust for blank lines
        if file_list_index >= 0 and file_list_index < len(self.file_list):
            self.file_display.selection_clear(0, tk.END)
            self.file_display.selection_set(listbox_index)
            self.drag_data["item"] = self.file_list[file_list_index]
            self.drag_data["index"] = file_list_index
            self.drag_data["label"] = tk.Label(widget, text=f"{file_list_index + 1}. {os.path.basename(self.file_list[file_list_index])}", relief='solid')
            self.drag_data["label"].place(x=event.x_root - widget.winfo_rootx() + self.label_offset_x, y=event.y_root - widget.winfo_rooty() + self.label_offset_y)

    def do_drag(self, event):
        if self.drag_data["item"]:
            self.drag_data["label"].place(x=event.x_root - self.root.winfo_rootx() + self.label_offset_x, y=event.y_root - self.root.winfo_rooty() + self.label_offset_y)
            widget = event.widget
            listbox_index = widget.nearest(event.y)
            file_list_index = listbox_index // 2  # Adjust for blank lines
            if self.drag_data["highlight"] is not None:
                self.file_display.itemconfig(self.drag_data["highlight"], {'bg': 'white'})
            if file_list_index >= 0 and file_list_index < len(self.file_list):
                self.file_display.itemconfig(listbox_index, {'bg': 'lightblue'})
                self.drag_data["highlight"] = listbox_index

    def stop_drag(self, event):
        if self.drag_data["item"]:
            widget = event.widget
            listbox_index = widget.nearest(event.y)
            new_file_list_index = listbox_index // 2  # Adjust for blank lines
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
            file_list_index = listbox_index // 2  # Adjust for blank lines
            if file_list_index > 0:
                self.file_list.insert(file_list_index - 1, self.file_list.pop(file_list_index))
                self.update_display()
                self.file_display.selection_set((file_list_index - 1) * 2)

    def move_down(self):
        selection = self.file_display.curselection()
        if selection:
            listbox_index = selection[0]
            file_list_index = listbox_index // 2  # Adjust for blank lines
            if file_list_index < len(self.file_list) - 1:
                self.file_list.insert(file_list_index + 1, self.file_list.pop(file_list_index))
                self.update_display()
                self.file_display.selection_set((file_list_index + 1) * 2)

    def update_display(self):
        self.file_display.delete(0, tk.END)
        for index, file_path in enumerate(self.file_list):
            filename = os.path.basename(file_path)
            self.file_display.insert(tk.END, f"{index + 1}. {filename}")
            self.file_display.insert(tk.END, "")  # Add a blank line for spacing


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileRearrangerApp(root)
    root.mainloop()
