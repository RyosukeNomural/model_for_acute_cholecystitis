# dicom to gray images

import os
import logging
import pydicom
from PIL import Image
import numpy as np

# Suppress pydicom warnings
logging.getLogger("pydicom").setLevel(logging.ERROR)

def clean_specific_character_set(ds):
    if "SpecificCharacterSet" not in ds:
        return ds
    enc = ds.SpecificCharacterSet
    if isinstance(enc, (str, bytes)):
        enc_list = [enc]
    else:
        enc_list = list(enc)
    cleaned = [e for e in enc_list if str(e).strip() != ""]
    if cleaned:
        ds.SpecificCharacterSet = cleaned
    else:
        del ds.SpecificCharacterSet
    return ds

def get_hu_values(dicom_data):
    image = dicom_data.pixel_array.astype(np.int16)
    intercept = getattr(dicom_data, "RescaleIntercept", 0)
    slope = getattr(dicom_data, "RescaleSlope", 1)
    return image * slope + intercept

def window_and_normalize_to_uint8(hu_image, min_hu, max_hu):
    """Apply HU windowing [min_hu, max_hu] and normalize to 0–255 uint8"""
    x = np.clip(hu_image, min_hu, max_hu).astype(np.float32)
    if max_hu > min_hu:
        x = (x - min_hu) / (max_hu - min_hu) * 255.0
    else:
        x[:] = 0
    return x.astype(np.uint8)

def convert_dcm_to_grayscale_image(dicom_path, output_path, window):
    """Convert a DICOM file to a grayscale image and save it"""
    try:
        dicom_data = pydicom.dcmread(dicom_path, force=True)
        dicom_data = clean_specific_character_set(dicom_data)

        print(f"Processing: {dicom_path}")

        hu_image = get_hu_values(dicom_data)

        # Convert to grayscale using a single HU window
        gray = window_and_normalize_to_uint8(hu_image, window[0], window[1])

        # Save using PIL (L = 8-bit grayscale)
        img = Image.fromarray(gray, mode="L")

        # PNG is recommended (JPEG may degrade medical image quality)
        img.save(output_path)
        print(f"Converted {dicom_path} to {output_path}")

    except Exception as e:
        print(f"Failed to convert {dicom_path}: {e}")

def process_dicom_in_directories(input_root, output_root, window):
    for root, dirs, files in os.walk(input_root):
        relative_path = os.path.relpath(root, input_root)
        output_dir = os.path.join(output_root, relative_path)
        os.makedirs(output_dir, exist_ok=True)

        dicom_files = [f for f in files if f.lower().endswith(".dcm")]
        for filename in dicom_files:
            dicom_path = os.path.join(root, filename)
            file_base_name = os.path.splitext(filename)[0]

            # PNG extension is recommended
            output_path = os.path.join(output_dir, f"{file_base_name}_gray.png")
            convert_dcm_to_grayscale_image(dicom_path, output_path, window)

# ===== Example usage =====
# For gallbladder (soft tissue), start with this window (adjust as needed)
window = (-70, 170)  # Example: covers fat to soft tissue to moderately high HU

#input_directory = f"{root}/DICOM normal"
#output_directory = f"{root}/GRAY/normal"
process_dicom_in_directories(input_directory, output_directory, window)

#input_directory = f"{root}/DICOM cholecystitis"
#output_directory = f"{root}/GRAY/cholecystitis"
process_dicom_in_directories(input_directory, output_directory, window)