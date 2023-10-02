import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from i18n import init_i18n, _


def on_button_click(entry):
    message = _("Hello, {name}!").format(name=entry.get())
    messagebox.showinfo(_("Greeting"), message)


class PhotoCollector:
    def __init__(self) -> None:
        self.source_directory = ""

    def select_source_directory(self):
        self.source_directory = filedialog.askdirectory(title="Select a Directory")
        if self.source_directory:
            self.selected_folder_entry.delete(0, tk.END)
            self.selected_folder_entry.insert(0, self.source_directory)

    def create_gui(self):
        window = tk.Tk()
        window.title(_("Collect Photoes Automatically"))

        # source directory
        selected_folder_label = tk.Label(window, text=_("Source Directory"))
        selected_folder_label.pack(pady=10)
        self.selected_folder_entry = tk.Entry(window, width=50)
        self.selected_folder_entry.pack(pady=10)
        button = tk.Button(window, text=_("Select Directory"), command=self.select_source_directory)
        button.pack(pady=20)

        window.mainloop()


if __name__ == "__main__":
    init_i18n('photo_collector', 'ja')  # Set the desired locale
    photo_collector = PhotoCollector()
    photo_collector.create_gui()
