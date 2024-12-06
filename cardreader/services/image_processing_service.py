import numpy as np
import cv2
from matplotlib import pyplot as plt
from rembg import remove

class ImageProcessingService:

    def crop_image(self, image, y: tuple[float, float], x: tuple[float, float]):
        h, w = image.shape[:2]

        cropped_image = image[int(y[0] * h):int(y[1] * h), int(x[0] * w):int(x[1] * w)]
        return cropped_image

    def imshow(self,  image, size= 10):
        h, w = image.shape[0], image.shape[1]
        aspect_ratio = w / h
        plt.figure(figsize=(size * aspect_ratio, size))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()

    def preprocess_image(self, image, ksize, treshold= 100, otsu = False):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        noise_removed_image = cv2.GaussianBlur(gray_image, (ksize, ksize), 0)
        resized_image = cv2.resize(noise_removed_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        if(otsu):
            _, binary_image = cv2.threshold(resized_image, treshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, binary_image = cv2.threshold(resized_image, treshold, 255, cv2.THRESH_BINARY)
        return binary_image

    def remove_background(self, image):
        output = remove(image)

        output_bw = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

        mask = np.where(output_bw < 20, 0, 255).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        # cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel, iterations=3)

        (x, y, w, h) = cv2.boundingRect(cleaned_mask)
        cropped_image = image[y:(y + h), x:(x + w)]
        self.imshow(cropped_image)
        return cropped_image