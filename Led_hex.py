import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json


class LEDPanelSimulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LED Panel Bitmap Generator")

        # Default configuration
        self.width = 32
        self.height = 16
        self.led_size = 20
        self.led_spacing = 2

        # State
        self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.drawing = False
        self.draw_mode = 1  # 1 for draw, 0 for erase

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - LED Display
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=(0, 10))

        # Control panel
        control_frame = tk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Dimension controls
        dim_frame = tk.Frame(control_frame)
        dim_frame.pack(fill=tk.X)

        tk.Label(dim_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="32")
        width_spin = tk.Spinbox(dim_frame, from_=8, to=64, textvariable=self.width_var, width=5)
        width_spin.pack(side=tk.LEFT, padx=5)

        tk.Label(dim_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.height_var = tk.StringVar(value="16")
        height_spin = tk.Spinbox(dim_frame, from_=8, to=64, textvariable=self.height_var, width=5)
        height_spin.pack(side=tk.LEFT, padx=5)

        tk.Button(dim_frame, text="Resize", command=self.resize_panel).pack(side=tk.LEFT, padx=5)

        # Tool buttons
        tool_frame = tk.Frame(control_frame)
        tool_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(tool_frame, text="✏️ Draw", command=lambda: self.set_mode(1),
                  bg='lightblue', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(tool_frame, text="🧹 Erase", command=lambda: self.set_mode(0),
                  bg='lightcoral', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(tool_frame, text="🗑️ Clear", command=self.clear_panel,
                  bg='lightyellow', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(tool_frame, text="🔄 Invert", command=self.invert_panel,
                  bg='lightgreen', width=8).pack(side=tk.LEFT, padx=2)

        # Canvas frame with border
        canvas_frame = tk.Frame(left_frame, bd=2, relief=tk.SUNKEN, bg='#1a1a1a')
        canvas_frame.pack()

        # LED Canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Right panel - Code output
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Variable name input
        name_frame = tk.Frame(right_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(name_frame, text="Variable Name:").pack(side=tk.LEFT)
        self.var_name = tk.StringVar(value="led_pattern")
        tk.Entry(name_frame, textvariable=self.var_name, width=20).pack(side=tk.LEFT, padx=5)

        # Generate button
        tk.Button(name_frame, text="⚡ Generate Code", command=self.generate_code,
                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                  width=15).pack(side=tk.LEFT, padx=5)

        # Code output area
        tk.Label(right_frame, text="Generated C++ Code:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.code_output = scrolledtext.ScrolledText(right_frame, width=50, height=25,
                                                     font=('Courier', 9))
        self.code_output.pack(fill=tk.BOTH, expand=True, pady=5)

        # File operations
        file_frame = tk.Frame(right_frame)
        file_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Button(file_frame, text="💾 Save Pattern", command=self.save_pattern).pack(side=tk.LEFT, padx=2)
        tk.Button(file_frame, text="📂 Load Pattern", command=self.load_pattern).pack(side=tk.LEFT, padx=2)
        tk.Button(file_frame, text="📄 Export to File", command=self.export_code).pack(side=tk.LEFT, padx=2)
        tk.Button(file_frame, text="📋 Copy Code", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)

        # Initialize panel
        self.create_led_panel()

    def create_led_panel(self):
        """Create the LED panel grid with SQUARE LEDs"""
        total_width = self.width * (self.led_size + self.led_spacing) + self.led_spacing
        total_height = self.height * (self.led_size + self.led_spacing) + self.led_spacing

        self.canvas.config(width=total_width, height=total_height)
        self.canvas.delete("all")

        # Create SQUARE LED rectangles
        for row in range(self.height):
            for col in range(self.width):
                x = col * (self.led_size + self.led_spacing) + self.led_spacing
                y = row * (self.led_size + self.led_spacing) + self.led_spacing

                # LED off color (dark)
                color = '#333333'
                if self.bitmap[row][col] == 1:
                    color = '#FF0000'  # LED on color (red)

                # Create SQUARE LED using rectangle
                led = self.canvas.create_rectangle(
                    x, y,
                    x + self.led_size,
                    y + self.led_size,
                    fill=color,
                    outline='#555555',
                    tags=f"led_{row}_{col}"
                )

    def get_led_position(self, event):
        """Convert mouse position to LED grid position"""
        col = (event.x - self.led_spacing) // (self.led_size + self.led_spacing)
        row = (event.y - self.led_spacing) // (self.led_size + self.led_spacing)

        if 0 <= row < self.height and 0 <= col < self.width:
            return row, col
        return None, None

    def toggle_led(self, row, col, mode=None):
        """Toggle LED on/off"""
        if row is None or col is None:
            return

        if mode is None:
            mode = self.draw_mode

        if self.bitmap[row][col] != mode:
            self.bitmap[row][col] = mode
            color = '#FF0000' if mode == 1 else '#333333'
            self.canvas.itemconfig(f"led_{row}_{col}", fill=color)

    def on_mouse_down(self, event):
        self.drawing = True
        row, col = self.get_led_position(event)
        self.toggle_led(row, col)

    def on_mouse_drag(self, event):
        if self.drawing:
            row, col = self.get_led_position(event)
            self.toggle_led(row, col)

    def on_mouse_up(self, event):
        self.drawing = False

    def set_mode(self, mode):
        """Set draw or erase mode"""
        self.draw_mode = mode

    def clear_panel(self):
        """Clear all LEDs"""
        self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.create_led_panel()

    def invert_panel(self):
        """Invert all LEDs"""
        for row in range(self.height):
            for col in range(self.width):
                self.bitmap[row][col] = 1 - self.bitmap[row][col]
        self.create_led_panel()

    def resize_panel(self):
        """Resize the LED panel"""
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())

            if 8 <= new_width <= 64 and 8 <= new_height <= 64:
                self.width = new_width
                self.height = new_height
                self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]
                self.create_led_panel()
            else:
                messagebox.showerror("Error", "Dimensions must be between 8 and 64")
        except ValueError:
            messagebox.showerror("Error", "Invalid dimensions")

    def generate_code(self):
        """Generate C++ code and display in terminal and text box"""
        var_name = self.var_name.get()

        # Generate C++ array
        code = f"// {self.width}x{self.height} LED Pattern\n"
        code += f"const uint8_t {var_name}[{self.height}][{self.width}] = {{\n"

        for row in self.bitmap:
            row_str = "  {" + ",".join(str(val) for val in row) + "}"
            code += row_str + ",\n"

        code = code.rstrip(",\n") + "\n};\n"

        # Display in text box
        self.code_output.delete('1.0', tk.END)
        self.code_output.insert('1.0', code)

        # Print to terminal
        print("\n" + "=" * 60)
        print("GENERATED LED PATTERN CODE")
        print("=" * 60)
        print(code)
        print("=" * 60 + "\n")

        messagebox.showinfo("Success", "Code generated! Check terminal and text box.")

    def save_pattern(self):
        """Save pattern to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            data = {
                'width': self.width,
                'height': self.height,
                'pattern': self.bitmap
            }
            with open(filename, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Success", f"Pattern saved to {filename}")

    def load_pattern(self):
        """Load pattern from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.width = data['width']
            self.height = data['height']
            self.bitmap = data['pattern']

            self.width_var.set(str(self.width))
            self.height_var.set(str(self.height))

            self.create_led_panel()
            messagebox.showinfo("Success", "Pattern loaded!")

    def export_code(self):
        """Export code to .h file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".h",
            filetypes=[("Header files", "*.h"), ("C++ files", "*.cpp"), ("All files", "*.*")]
        )

        if filename:
            var_name = self.var_name.get()

            code = f"// {self.width}x{self.height} LED Pattern\n"
            code += f"// Generated by LED Panel Simulator\n\n"
            code += f"#ifndef {var_name.upper()}_H\n"
            code += f"#define {var_name.upper()}_H\n\n"
            code += f"#include <stdint.h>\n\n"
            code += f"const uint8_t {var_name}[{self.height}][{self.width}] = {{\n"

            for row in self.bitmap:
                row_str = "  {" + ",".join(str(val) for val in row) + "}"
                code += row_str + ",\n"

            code = code.rstrip(",\n") + "\n};\n\n"
            code += f"#endif // {var_name.upper()}_H\n"

            with open(filename, 'w') as f:
                f.write(code)

            messagebox.showinfo("Success", f"Code exported to {filename}")

    def copy_to_clipboard(self):
        """Copy generated code to clipboard"""
        code = self.code_output.get('1.0', tk.END)
        if code.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Success", "Code copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "Generate code first!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    simulator = LEDPanelSimulator()
    simulator.run()