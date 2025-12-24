import customtkinter as ctk
import queue

class LamaGUI(ctk.CTk):
    def __init__(self, task_queue, response_queue):
        super().__init__()

        # Queue connections (Coming from Main.py)
        self.task_queue = task_queue
        self.response_queue = response_queue

        # Window settings
        self.title("LAMA v7.0 - Modular Architecture")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")

        self.setup_ui()

        # Start listening to the queue (Every 100ms)
        self.after(100, self.check_queue)

    def setup_ui(self):
        # Simple layout
        self.chat_area = ctk.CTkScrollableFrame(self, width=900, height=500)
        self.chat_area.pack(pady=20, padx=20, fill="both", expand=True)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type something...", height=40)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side="right")

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg: return

        # 1. Write message to screen
        self.log_message("YOU", msg, "blue")
        self.entry.delete(0, "end")

        # 2. Put task in queue (Backend processes it)
        self.task_queue.put(msg)

    def log_message(self, sender, text, color="gray"):
        msg_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        msg_frame.pack(pady=5, fill="x")

        lbl = ctk.CTkLabel(msg_frame, text=f"{sender}: {text}",
                           fg_color=color if color != "gray" else "transparent",
                           corner_radius=10, text_color="white", anchor="w", justify="left", wraplength=800)
        lbl.pack(fill="x", padx=10, pady=2)

    def check_queue(self):
        """Checks for response from background"""
        try:
            while True:
                # Get data from queue (non-blocking)
                message_type, content = self.response_queue.get_nowait()

                if message_type == "AI":
                    self.log_message("LAMA", content, "#2d2d2d")
                elif message_type == "SYSTEM":
                    self.log_message("SYSTEM", content, "#3a3a3a")
                elif message_type == "ERROR":
                    self.log_message("ERROR", content, "red")

        except queue.Empty:
            pass
        finally:
            # Check again after 100ms
            self.after(100, self.check_queue)
