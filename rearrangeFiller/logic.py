# logic.py

import os
import shutil
import re
from tkinter import messagebox


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
                # Copy new files to the original folder
                for index, file_path in enumerate(self.file_list):
                    filename = f"{index + 1}. {os.path.basename(file_path)}"
                    dest_path = os.path.join(self.original_folder, filename)

                    file_path = os.path.normpath(file_path)
                    dest_path = os.path.normpath(dest_path)

                    if os.path.exists(dest_path):
                        os.remove(dest_path)  # Delete the old file if it exists

                    shutil.copy2(file_path, dest_path)

                # Remove old files that are no longer in the list of new files
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

        # Rename the file in the original folder
        if file_path != new_path:
            os.rename(file_path, new_path)

        return new_path
