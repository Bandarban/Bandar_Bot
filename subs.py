import random
import time
import copy
import moviepy.editor as mpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont, GifImagePlugin
import cv2


def get_text_bbox(text: str, font_path: str) -> Image:
    """
    Возвращает изображение текста в минимальном описывающем прямоугольнике.
    :param font_path: название шрифта.
    :param text: текст.
    :return: изображение текста.
    """
    text_image = Image.new('L', (1000, 1000))
    brush = ImageDraw.Draw(text_image)
    font = ImageFont.truetype(font_path, 95)
    brush.text((50, 50), text, font=font, fill=255)
    x1, y1, x2, y2 = Image.Image.getbbox(text_image)
    text_image = text_image.crop((x1, y1, x2, y2))
    return text_image


def get_result_image(bbox_image: Image, image_height: int, image_width: int) -> Image:
    """
    Создает финальное изображение.
    :param bbox_image: изображение текста в минимальном описывающем прямоугольнике.
    :param image_height: высота изоюражения.
    :param image_width: ширина изображения.
    :return: возвращает изображение, которое должно получиться в итоге.
    """
    # Фон изображения
    background = Image.new('RGBA', (image_width, image_height), "#00ff00")
    alpha_layer = Image.new("L", (image_width, image_height), 0)
    background.putalpha(alpha_layer)
    # Создание текста
    y_offset = int(bbox_image.height / 2)
    x_offset = int(bbox_image.width / 2)
    # Нанесение текста на фон
    ImageDraw.Draw(background).bitmap((image_width / 2 - x_offset, image_height / 2 - y_offset), bbox_image)
    return background


def create_subscription_gif(text, font_path, image_height, image_width):
    """

    :param text:
    :param font_path:
    :param image_height:
    :param image_width:
    :return:
    """
    bbox_text = get_text_bbox(text, font_path)
    final_image = get_result_image(bbox_text, image_height, image_width)
    curren_image = Image.new('RGBA', (image_width, image_height), "#00ff00")
    alpha_layer = Image.new("L", (image_width, image_height), 0)
    curren_image.putalpha(alpha_layer)

    cv_bg = np.array(final_image)
    cv_dbg = np.array(curren_image)
    print(cv_dbg.shape)
    cv_dbg[:, :, 3] = cv_bg[:, :, 3]
    count = 0
    frames = []
    for i in range(0, cv_dbg.shape[0], 1):
        cv_dbg[i:i + 1, :, :] = cv_bg[i:i + 1, :, :]
        # cv2.imshow("asd", cv_dbg)
        # cv2.waitKey(10)
        frames.append(copy.copy(cv_dbg))
    temp = [frames[-1]]*20
    frames.extend(temp)
    clip = mpy.ImageSequenceClip(frames, fps=30, durations=10)
    clip.write_gif("follower.gif", fps=30, loop=0)
    time.sleep(10)
    clip = mpy.ImageSequenceClip(frames[0:1], fps=30, durations=10)
    clip.write_gif("follower.gif", fps=30, loop=0)





# create_subscription_gif("VASYAN SUPER PRO", "fonts/Monserga-regular-FFP.ttf", 250, 800)

# cv2.imshow("asd", image)
# cv2.waitKey()
