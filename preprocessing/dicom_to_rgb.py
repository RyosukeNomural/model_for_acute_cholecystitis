# DICOM to RGB

import os
import logging
import pydicom
from PIL import Image
import numpy as np

logging.getLogger("pydicom").setLevel(logging.ERROR)

def clean_specific_character_set(ds):
    """Remove invalid or empty entries from SpecificCharacterSet"""
    if "SpecificCharacterSet" not in ds:
        return ds

    enc = ds.SpecificCharacterSet

    # Handle both string and list formats
    if isinstance(enc, (str, bytes)):
        enc_list = [enc]
    else:
        enc_list = list(enc)

    # Remove empty or whitespace-only elements
    cleaned = [e for e in enc_list if str(e).strip() != ""]

    if cleaned:
        ds.SpecificCharacterSet = cleaned
    else:
        # If all entries are removed, delete the tag itself
        del ds.SpecificCharacterSet

    return ds


def get_hu_values(dicom_data):
    """Extract Hounsfield Unit (HU) values from DICOM data"""
    image = dicom_data.pixel_array.astype(np.int16)
    intercept = getattr(dicom_data, "RescaleIntercept", 0)
    slope = getattr(dicom_data, "RescaleSlope", 1)
    return image * slope + intercept


def filter_hu_range(hu_image, min_hu, max_hu):
    """Extract pixels within a specified HU range and normalize to 0–255"""
    filtered_image = np.clip(hu_image, min_hu, max_hu)
    if filtered_image.max() > filtered_image.min():
        filtered_image = (filtered_image - min_hu) / (max_hu - min_hu) * 255
    else:
        filtered_image = np.zeros_like(filtered_image)
    return filtered_image.astype(np.uint8)


def convert_dcm_to_rgb_image(dicom_path, output_path, ranges):
    """Convert a DICOM file into an RGB image"""
    try:
        # ❷ Read with force=True (allows loading even partially corrupted files)
        dicom_data = pydicom.dcmread(dicom_path, force=True)

        # ❸ Clean SpecificCharacterSet after loading
        dicom_data = clean_specific_character_set(dicom_data)

        print(f"Processing: {dicom_path}")

        hu_image = get_hu_values(dicom_data)

        # Apply filtering for each HU range
        r_channel = filter_hu_range(hu_image, *ranges[0])
        g_channel = filter_hu_range(hu_image, *ranges[1])
        b_channel = filter_hu_range(hu_image, *ranges[2])

        # Create RGB image
        rgb_image = np.stack([r_channel, g_channel, b_channel], axis=-1)

        # Save image
        image = Image.fromarray(rgb_image)
        image.save(output_path)
        print(f"Converted {dicom_path} to {output_path}")
    except Exception as e:
        print(f"Failed to convert {dicom_path}: {e}")


def process_dicom_in_directories(input_root, output_root, ranges):
    """Process all DICOM files within the parent directory"""
    for root, dirs, files in os.walk(input_root):
        relative_path = os.path.relpath(root, input_root)
        output_dir = os.path.join(output_root, relative_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Process DICOM files
        dicom_files = [f for f in files if f.lower().endswith(".dcm")]
        for filename in dicom_files:
            dicom_path = os.path.join(root, filename)
            file_base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{file_base_name}_rgb.jpeg")
            convert_dcm_to_rgb_image(dicom_path, output_path, ranges)


# Example usage
ranges = [(-70, 50), (-10, 110), (50, 170)]  # HU ranges for R, G, B channels
input_directory = f"{root}/DICOM normal"
output_directory = f"{root}/RGB/normal"

process_dicom_in_directories(input_directory, output_directory, ranges)

input_directory = f"{root}/DICOM cholecystitis"
output_directory = f"{root}/RGB/cholecystitis"

process_dicom_in_directories(input_directory, output_directory, ranges)