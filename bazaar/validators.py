import os
from django.core.exceptions import ValidationError
from PIL import Image

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def validate_image_file(file_obj):
    """
    Validates uploaded image file:
    1. Checks file size (<= 5MB)
    2. Checks file extension (.jpg, .jpeg, .png, .webp)
    3. Validates actual image data with Pillow to prevent arbitrary file upload attacks.
    """
    if not file_obj:
        return

    # 1. Size check
    if file_obj.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"File size exceeds 5MB limit (File size: {file_obj.size / (1024*1024):.2f}MB).")

    # 2. Extension check
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")

    # 3. Content verification using Pillow
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.verify()  # Verify image integrity without decoding full pixels
        file_obj.seek(0)
    except Exception as e:
        raise ValidationError("Uploaded file is not a valid or readable image.")
