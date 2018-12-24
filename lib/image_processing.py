import os
import time
from pytesseract import pytesseract
from PIL import Image, ImageEnhance

import cv2
import numpy as np


class Image_Processing:
    def __init__(self):
        self.filetype = ".png"
        self.filepath = "./tmp/"
        self.resize_size = 3
        self.enhance_by = 30.0
        # check if the dir exist else create it
        if not os.path.isdir(self.filepath):
            os.makedirs(self.filepath)

    def checkImageOrObject(self, src_image):
        """
        This function will check if the src_image passed to this function is filepath or image file object.
        if image file path found it will open file and return file object else return image file object
        :param src_image:
        :return: return image file object
        """

        try:
            if type(src_image) == str:
                if not os.path.exists(src_image):
                    print(src_image + " : invalid image path given ")
                    return False
                else:
                    return Image.open(src_image)
            else:
                return src_image

        except Exception as e:
            print(e)

    def imageCleaner(
        self, src_image, resize_size=3, enhance_by=30.0, filename=time.time()
    ):
        """
        This function will clean the image
        i.e - it will resize the image by 3 times
            - sharpen the image
            - invert the image(black and white image)
        :param src_image_object: source image object
        :param resize_size: zoomout image by (default 3) (optional)
        :param enhance_by: enhance rate (default 30.0) (optional)
        :param filename: cleaned image save to this filename (optional)
        :return: dictionary with image_object & image_path
        """

        self.src_image_object = self.checkImageOrObject(src_image)

        if self.src_image_object:
            try:
                print("ImageCleaner method initializing")
                src_image = self.src_image_object.resize(
                    (
                        self.src_image_object.width * resize_size,
                        self.src_image_object.height * resize_size,
                    ),
                    Image.ANTIALIAS,
                )
                enhancer = ImageEnhance.Sharpness(src_image)
                src_image = enhancer.enhance(enhance_by)
                print("Image enhance completed")
                src_image = src_image.convert("L")

                src_image = src_image.point(lambda x: 0 if x < 175 else 255, "1")
                # src_image   = src_image.point(range(256, 0, -1) * 3)

                FQ_filename = "{}{}.png".format(self.filepath, filename)
                src_image.save(FQ_filename)
                print("Image Cleaning completed")

                return {"image_object": src_image, "image_path": FQ_filename}

            except Exception as e:
                print(e)
        else:
            pass

    def ocr(self, image_path):
        """
        This is tesseract ocr function which will extract text from image
        :param image_path:
        :return: list of extracted strings
        """
        src_image_object = self.imageCleaner(
            image_path, self.resize_size, self.enhance_by
        )["image_object"]
        try:
            print("ExtractTextFromImage method initializing")
            text_str = pytesseract.image_to_string(src_image_object)
            str_list = text_str.split("\n")
            str_list = list(filter(None, str_list))  # remove empty string
            return str_list
        except Exception as e:
            print(e)

    def image_coordinates(
        self, image_path="./tmp/full_img.png", subimage_path="./tmp/sub_img.png"
    ):
        """
        This function will find the co-ordinates of sub image in parent image
        :param image_path:  fullpage screenshot
        :param subimage_path: component image in that screenshot
        :return: dict with center x,y co-ordinates on fullpage screenshot image
        """
        img = cv2.imread(image_path)
        sub_img = cv2.imread(subimage_path)

        height, width, channels = sub_img.shape

        result = cv2.matchTemplate(img, sub_img, cv2.TM_CCOEFF_NORMED)
        co_ordinates = np.unravel_index(result.argmax(), result.shape)

        return {"x": co_ordinates[1] + width / 2, "y": co_ordinates[0] + height / 2}


if __name__ == "__main__":
    print("In Image Processing class")
