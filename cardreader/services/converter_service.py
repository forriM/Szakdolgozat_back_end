import base64
import uuid
from io import BytesIO

import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.utils import timezone


class ConverterService:
    def base64_to_file(self, image_string):
        """
        Converts a base64 image string into a Django ContentFile.
        """
        file_format, img_str = image_string.split(';base64,')  # Get the content type
        image_bytes = base64.b64decode(img_str)  # Decode the base64 string
        image_file = BytesIO(image_bytes)

        # Generate a unique filename
        ext = file_format.split('/')[-1]  # Get the file extension (e.g., 'jpeg' or 'png')
        unique_filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}.{ext}"

        image_file = ContentFile(image_bytes, name=unique_filename)

        return image_file

    def file_to_numpy(self, file):
        """
        Converts a file-like object to a NumPy array using OpenCV.
        """
        image_np = np.frombuffer(file.read(), np.uint8)

        # Decode the NumPy array into an image (OpenCV format)
        image_array = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image_array is None:
            raise ValueError("Could not decode the image from the file object")

        return image_array

    def numpy_to_file(self, image_array):
        """
        Converts a NumPy array to a Django ContentFile.
        """
        # Encode the NumPy array into an image format in memory
        success, image_encoded = cv2.imencode('.jpeg', image_array)

        if not success:
            raise ValueError("Could not encode image array")

        # Convert the encoded image to a BytesIO object
        image_bytes = image_encoded.tobytes()
        unique_filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}.jpeg"

        # Optionally, set the file name or extension for the file-like object
        image_file = ContentFile(image_bytes, name=unique_filename)

        return image_file

    def base64_to_numpy(self, image_string):
        """
        Converts a base64 image string into a NumPy array.
        """
        # Decode the base64 string to get the image bytes
        file_format, img_str = image_string.split(';base64,')  # Get the content type
        image_data = base64.b64decode(img_str)

        # Convert the bytes into a BytesIO object
        image_file = BytesIO(image_data)

        # Convert the BytesIO object to a NumPy array
        image_np = np.frombuffer(image_file.read(), np.uint8)

        return image_np
