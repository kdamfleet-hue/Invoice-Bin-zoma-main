import os
from PIL import Image

def make_transparent(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    # Using a threshold for near-white
    for item in data:
        # item is (R, G, B, A)
        r, g, b, a = item
        # If the pixel is close to white, make it transparent
        # Calculate grayscale distance to white
        if r > 230 and g > 230 and b > 230:
            # We can do a smooth alpha or just full transparency.
            # Let's do full transparency for near white to be safe
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Saved transparent image to {output_path}")

input_1 = r"C:\Users\user\.gemini\antigravity-ide\brain\08239573-f380-475a-8951-1045b14a89b0\media__1781652393295.jpg"
input_2 = r"C:\Users\user\.gemini\antigravity-ide\brain\08239573-f380-475a-8951-1045b14a89b0\media__1781652470319.jpg"

output_1 = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\static\nav_logo.png"
output_2 = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\static\main_logo.png"

make_transparent(input_1, output_1)
make_transparent(input_2, output_2)
