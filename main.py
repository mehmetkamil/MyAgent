import threading
import queue
import gui
import brain
import automation
import time

def backend_loop(task_queue, response_queue):
    response_queue.put(("SYSTEM", "System starting..."))

    try:
        my_brain = brain.LamaBrain()
        my_automation = automation.AutomationAgent()
        response_queue.put(("SYSTEM", "LAMA v7 (Smart Mode) Ready!"))
    except Exception as e:
        response_queue.put(("ERROR", f"Startup error: {e}"))
        return

    while True:
        try:
            # Wait for task
            user_input = task_queue.get()

            # 1. Ask Brain (Will it return Text or Tool?)
            response_queue.put(("SYSTEM", "Thinking..."))
            response_type, content = my_brain.think(user_input)

            # 2. Process Response
            if response_type == "text":
                # Normal chat
                response_queue.put(("AI", content))

            elif response_type == "tool_call":
                # A command arrived!
                tool_name = content["name"]
                tool_args = content["args"]

                # Inform user
                response_queue.put(("SYSTEM", f"Processing: {tool_name}"))

                # Execute automation
                result = my_automation.execute_tool_call(tool_name, tool_args)

                # Write result
                response_queue.put(("SYSTEM", result))

        except Exception as e:
            response_queue.put(("ERROR", f"Processing error: {e}"))

if __name__ == "__main__":
    task_queue = queue.Queue()
    response_queue = queue.Queue()

    backend_thread = threading.Thread(target=backend_loop, args=(task_queue, response_queue), daemon=True)
    backend_thread.start()

    app = gui.LamaGUI(task_queue, response_queue)
    app.mainloop()
