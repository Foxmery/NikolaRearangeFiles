# main.py

from tkinterdnd2 import TkinterDnD
from rearrangeFiller.GUI import FileRearrangerApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileRearrangerApp(root)
    root.mainloop()
