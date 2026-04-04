from rembg import remove
from PIL import Image
import io
import numpy as np
import cv2

PRESETS = {
    "us_passport": (600, 600),  # 2x2 inch at 300dpi
    "schengen_visa": (413, 531),  # 35x45mm at 300dpi
    "resume": (450, 600)
}

def detect_face_center(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None, None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        return x + w // 2, y + h // 2
    return img.shape[1] // 2, img.shape[0] // 2

def process_id_photo(image_bytes, bg_color_hex="#FFFFFF", preset_key="us_passport"):
    target_size = PRESETS.get(preset_key, PRESETS["us_passport"])
    
    face_x, face_y = detect_face_center(image_bytes)
    
    input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    output_image = remove(input_image)
    
    background = Image.new("RGBA", target_size, bg_color_hex)
    
    person_width, person_height = output_image.size
    scale = min(target_size[0] / person_width, target_size[1] / person_height) * 0.85
    new_size = (int(person_width * scale), int(person_height * scale))
    resized_person = output_image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Center the face at 40% from top
    target_face_y = target_size[1] * 0.4
    y_offset = int(target_face_y - (face_y / person_height) * new_size[1])
    x = (target_size[0] - new_size[0]) // 2
    y = max(0, y_offset)
    
    background.paste(resized_person, (x, y), resized_person)
    final_image = background.convert("RGB")
    
    img_byte_arr = io.BytesIO()
    final_image.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr