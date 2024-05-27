import cv2
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import svgwrite
import base64
from io import BytesIO
import subprocess  # Import subprocess for opening Inkscape

class EmbeddedUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Draw App")

        # Live Preview Frame
        self.live_preview_frame = ttk.Frame(root, padding=10)
        self.live_preview_frame.grid(row=0, column=0, sticky="nsew")

        self.live_preview_label = ttk.Label(self.live_preview_frame, text="Line Draw Canvas", font=("Helvetica", 14))
        self.live_preview_label.grid(row=0, column=0, pady=(0, 10))

        self.canvas = tk.Canvas(self.live_preview_frame, width=640, height=480, bg="#000")
        self.canvas.grid(row=1, column=0)

        # Controls Frame
        self.controls_frame = ttk.Frame(root, padding=10, style="Dark.TFrame")
        self.controls_frame.grid(row=0, column=1, sticky="nsew")

        # New button for image upload
        self.upload_button = ttk.Button(self.controls_frame, text="Upload Image", command=self.upload_image)
        self.upload_button.grid(row=0, column=0, pady=5)

        # Removed the capture button and retake image button

        self.linedraw = ttk.Button(self.controls_frame, text="Convert to Line Drawing", command=self.convert_to_line_drawing)
        self.linedraw.grid(row=1, column=0, pady=5)
        self.linedraw["state"] = tk.DISABLED

        self.convsvg = ttk.Button(self.controls_frame, text="Convert to SVG", command=self.convert_to_svg)
        self.convsvg.grid(row=2, column=0, pady=5)
        self.convsvg["state"] = tk.DISABLED

        self.save = ttk.Button(self.controls_frame, text="Save SVG", command=self.save_svg)
        self.save.grid(row=3, column=0, pady=5)
        self.save["state"] = tk.DISABLED

        self.openinkscape_button = ttk.Button(self.controls_frame, text="Open Inkscape", command=self.open_inkscape)
        self.openinkscape_button.grid(row=4, column=0, pady=5)

        ttk.Button(self.controls_frame, text="About", command=self.show_about_info).grid(row=5, column=0, pady=5)

        # Initialize variables
        self.image = None
        self.captured_image = None
        self.line_drawing = None
        self.svg_content = None
        self.photo_image_ref = None  # Reference to PhotoImage object
        self.cap = None

        # Commented out the call to start_live_preview
        # self.start_live_preview()

    # Removed the start_live_preview method

    # Removed the show_camera_preview method

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".png;.jpg;.jpeg;.gif")])
        if file_path:
            # Clear the canvas
            self.canvas.delete("all")

            # Removed the code related to stopping live camera preview
            self.captured_image = cv2.imread(file_path)
            height, width, _ = self.captured_image.shape

            # Resize the image to fit the canvas dimensions
            canvas_width = self.canvas.winfo_reqwidth()
            canvas_height = self.canvas.winfo_reqheight()

            if width > canvas_width or height > canvas_height:
                scale_factor = min(canvas_width / width, canvas_height / height)
                self.captured_image = cv2.resize(self.captured_image, (int(width * scale_factor), int(height * scale_factor)))

            self.photo_image_ref = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image_ref)

            # Disable the capture button after uploading an image
            # Removed the code related to disabling camera-related buttons
            self.convsvg["state"] = tk.DISABLED
            self.save["state"] = tk.DISABLED
            self.linedraw["state"] = tk.NORMAL

    # Removed the capture_image method

    # Removed the retake_image method

    def convert_to_line_drawing(self):
        if self.captured_image is not None:
            # Convert the image to grayscale
            gray_image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur to reduce noise
            blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
            # Apply edge detection using the Canny edge detector
            edged_image = cv2.Canny(blurred_image, 50, 150)

            # Display the edged image
            self.photo_image_ref = ImageTk.PhotoImage(Image.fromarray(edged_image))
            self.canvas.delete("all")  # Clear previous drawings on canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image_ref)

            # Save the line drawing for further processing if needed
            self.line_drawing = edged_image

            self.convsvg["state"] = tk.NORMAL
            self.save["state"] = tk.DISABLED
            self.linedraw["state"] = tk.DISABLED

    def convert_to_svg(self):
        if self.line_drawing is not None:
            # Remove the line drawing preview from the canvas
            if hasattr(self, 'photo_image_ref_line_drawing'):
                self.canvas.delete(self.photo_image_ref_line_drawing)

            inverted_image = cv2.bitwise_not(self.line_drawing)

            # Convert numpy array to Image
            img = Image.fromarray(inverted_image)

            # Convert image to base64 encoding
            img_pil = img.convert('RGBA')  # Convert to RGBA for transparency support
            img_io = BytesIO()
            img_pil.save(img_io, 'PNG')
            img_bytes = img_io.getvalue()
            base64_img = base64.b64encode(img_bytes).decode("utf-8")

            # Create SVG drawing
            dwg = svgwrite.Drawing(filename="output.svg", size=(img.width, img.height))

            # Create SVG image from base64 encoded image
            svg_img = dwg.image("data:image/png;base64," + base64_img, size=(img.width, img.height))
            svg_img.attribs['x'] = '0'
            svg_img.attribs['y'] = '0'
            dwg.add(svg_img)

            # Save SVG content
            self.svg_content = dwg.tostring()

            # Display SVG Image on the canvas
            self.photo_image_ref_svg = ImageTk.PhotoImage(img)
            self.canvas.delete("all")  # Clear previous drawings on canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image_ref_svg)

            self.convsvg["state"] = tk.DISABLED
            self.save["state"] = tk.NORMAL
            self.linedraw["state"] = tk.DISABLED

    def save_svg(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if file_path and self.svg_content is not None:
            with open(file_path, "w") as svg_file:
                svg_file.write(self.svg_content)

    # Removed the retake_image method

    def show_about_info(self):
        about_info = "This app is made by Dereena Benadict, Sreelakshmi Cheviri, Dalmeet Singh, Rahul Akkara"
        messagebox.showinfo("About", about_info)

    def open_inkscape(self):
        try:
            # Change the path to Inkscape executable based on your system
            inkscape_path = "/snap/bin/inkscape"  # Example path for Windows
            subprocess.Popen([inkscape_path])
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Inkscape: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EmbeddedUI(root)
    root.mainloop()