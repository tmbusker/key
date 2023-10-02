import tkinter as tk


def center_window(window, offsetx: int = 0, offsety: int = 0):
    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width - window.winfo_reqwidth()) // 2
    y = (screen_height - window.winfo_reqheight()) // 2

    if offsetx and x > offsetx:
        x -= offsetx
    if offsety and y > offsety:
        y -= offsety

    # Set the window's position
    window.geometry(f"+{x}+{y}")


class MessagePanel(tk.Frame):
    def __init__(self, width, height, master=None, max_lines=10):
        super().__init__(master)
        self.create_widgets(width, height)
        self.messages = []
        self.max_lines = max_lines

    def create_widgets(self, width, height):
        # Create a Text widget to display messages
        self.text_widget = tk.Text(self, width=width, height=height, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.Y)

        # Add a Scrollbar to the Text widget
        self.scrollbar = tk.Scrollbar(self, command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the Text widget to use the Scrollbar
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
        
        # Clear existing text
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, '\n'.join(self.messages))
        self.text_widget.yview(tk.END)

        # Update the Tkinter event loop to reflect changes
        self.update()
