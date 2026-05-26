from PIL import Image

# 1. Open your uploaded JPEG file
# Update the path to match where your image is stored on your computer
img = Image.open('static/media/hopehub_logo.jpeg').convert("RGBA")

datas = img.getdata()
newData = []

# 2. Loop through all pixels and turn white/near-white pixels transparent
for item in datas:
    # Captures pure white (255, 255, 255) and off-white/textured white pixels
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        newData.append((255, 255, 255, 0))  # 0 alpha means fully transparent
    else:
        newData.append(item)

# 3. Save the new image as a PNG
img.putdata(newData)
img.save('hopehub_logo.png', "PNG")
print("Conversion complete! Saved as aurora_logo.png")
