from paddleocr import PaddleOCR, draw_ocr
import os
import cv2
import matplotlib.pyplot as plt

img_path = "./images/image.png"

ocr = PaddleOCR(use_angle=True, lang="en")
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

# draw result
from PIL import Image

result = result[0]
image = Image.open(img_path).convert("RGB")
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores)
im_show = Image.fromarray(im_show)
im_show.save("result.jpg")
