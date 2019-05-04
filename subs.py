# coding=utf-8
import math
import random
import time
import moviepy.editor as mpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import colorsys


def get_text_bbox(text: str, font_path: str, box_size: tuple) -> Image:
    """
    Возвращает изображение текста в минимальном описывающем прямоугольнике.
    :param box_size: ширина и высота результирующего изображения с текстом.
    :param font_path: название шрифта.
    :param text: текст.
    :return: изображение текста.
    """
    text_image = Image.new('L', tuple(map(lambda x: x * 2, box_size)))
    brush = ImageDraw.Draw(text_image)
    font = ImageFont.truetype(font_path, 100)
    brush.text((50, 50), text, font=font, fill=255)
    x1, y1, x2, y2 = Image.Image.getbbox(text_image)
    text_image = text_image.crop((x1, y1, x2, y2))

    return text_image


def add_chromakey(bbox_image: Image.Image, box_size: tuple) -> Image:
    """
    Создает  изображение текста.
    :param box_size: размер изображения.
    :param bbox_image: изображение текста.
    :return: возвращает изображение, которое должно получиться в итоге.
    """
    # Фон изображения
    if bbox_image.width > box_size[0]:
        proportions = bbox_image.height / bbox_image.width
        bbox_image = bbox_image.resize((box_size[0] - 100, int((box_size[0] - 100) * proportions)))

    background = Image.new('RGB', box_size, "#000000")
    # Создание текста
    y_offset = int(bbox_image.height / 2)
    x_offset = int(bbox_image.width / 2)
    # Нанесение текста на фон
    color = colorsys.hsv_to_rgb(random.random(), 1, 1)
    color = tuple(map(lambda x: int(x * 255), color))
    ImageDraw.Draw(background).bitmap((box_size[0] / 2 - x_offset, box_size[1] / 2 - y_offset), bbox_image,
                                      fill=color)
    return background


def draw_circle(current_image: Image.Image,
                coordinate: list,
                radius: float = 40,
                bitmap: Image.Image = None,
                color: tuple = (0, 255, 255),
                density: float = 0.3):
    """

    :param current_image: изображение для рисования.
    :param coordinate: координата центра окружности.
    :param radius: радиус окружности.
    :param bitmap: Изображение для переноса.
    :param color: Цвет рисования.
    :param density: Плотность закрашивания.
    :return:
    """
    for x, y in get_circle_points(coordinate, radius):
        if random.random() <= density and x <= current_image.width and y <= current_image.height:
            try:
                if bitmap is None:
                    current_image.putpixel((x, y), value=color)
                else:
                    pixel_color = bitmap.getpixel(xy=(x, y))
                    if pixel_color != (0, 255, 0):
                        current_image.putpixel((x, y), value=pixel_color)
            except IndexError:
                pass


def get_circle_points(coordinate: list, radius: float) -> tuple:
    """
    Генератор, возвращаюй  точки находящиеся внутри окружности.
    :param coordinate: координаты центра окружности.
    :param radius: радиус окружности.
    :return: координаты точки, принадлежащшей данной окружности.
    """
    a, b = coordinate
    for y in range(int(b - radius), int(b + radius)):
        x1 = int(abs(math.sqrt(radius ** 2 - (y - b) ** 2) - a))
        x2 = int(2 * a - x1)
        for x in range(x1, x2):
            yield x, y


def get_path(start_position: tuple, end_position: tuple, step: int) -> tuple:
    """
    Составляет маршрут до конечной точки, формируя кривую линию.
    :param start_position: начальная позиция.
    :param end_position: конечная позиция.
    :param step: длина шага.
    :return: следующую позицию.
    """
    x1, y1 = start_position
    x2, y2 = end_position
    dx, dy = x2 - x1, y2 - y1
    if math.sqrt((dx ** 2) + dy ** 2) <= step:
        return end_position
    angle = math.atan2(dy, dx)
    angle += random.randint(-15, 15) * math.pi / 180
    new_x = x1 + step * math.cos(angle)
    new_y = y1 + step * math.sin(angle)
    return int(new_x), int(new_y)


def get_background_frames(image_size: tuple) -> list:
    """
    Создает кадры отрисовки заднего фона.
    :param image_size: размер изображения
    :return: список кадров.
    """
    current_image = Image.new('RGB', image_size, "#000000")
    radius = 20
    position = [100, 100]

    points = [(700, 100), (100, 150), (700, 150)]

    frames = [np.array(current_image)]
    color = colorsys.hsv_to_rgb(random.random(), 1, 1)
    color = tuple(map(lambda x: int(x * 255), color))

    for target in points:
        while position != target:
            draw_circle(current_image, position, radius=40, density=0.45, color=color)
            draw_circle(current_image, position, radius=60, density=0.25, color=color)
            position = get_path(position, target, int(radius / 2))
            cv2_img = np.array(current_image)
            frames.append(cv2_img)
    return frames


def draw_text_frames(text_bitmap: Image.Image, background_image: Image.Image) -> list:
    """
    Возвращает кадры отрисовки текста
    :param text_bitmap: изображение итогового текста.
    :param background_image: изображение фона.
    :return: список кадров анимации.
    """
    points = [(50, 200), (50, 50), (175, 200), (175, 50), (300, 200), (300, 50), (425, 200), (425, 50), (575, 200),
              (575, 50), (700, 200), (700, 50), (800, 200)]
    frames = []
    position = [50, 50]
    radius = 40
    for target in points:
        while position != target:
            draw_circle(background_image, position, radius=radius, density=1, bitmap=text_bitmap)
            position = get_path(position, target, int(radius / 2))
            cv2_img = np.array(background_image)
            frames.append(cv2_img)
    return frames


def render_gif(frames: list, duration: int, fps: int):
    frames = frames[::2]
    frames += [frames[-1]] * 200
    clip = mpy.ImageSequenceClip(frames, fps=fps, durations=1)
    clip.write_gif("follower.gif", fps=fps, loop=0)
    time.sleep(clip.duration)
    clip = mpy.ImageSequenceClip(frames[0:1], fps=30, durations=10)
    clip.write_gif("follower.gif", fps=30, loop=0)


def bgr_to_rgb(image):
    b, g, r = cv2.split(image)
    return cv2.merge((r, g, b))


def create_subscription_gif(text: str, font_path: str, image_size: tuple) -> None:
    """
    Создает гиф с хромакеем.
    :param image_size: ширина и высота изображения.
    :param text: текст изображения.
    :param font_path: путь до шрифта.
    :return:
    """
    bbox_text = get_text_bbox(text, font_path, image_size)
    chromakey_image = add_chromakey(bbox_text, image_size)
    background_frames = get_background_frames(image_size)
    last_image = background_frames[-1]
    last_image = Image.fromarray(last_image)
    text_frames = draw_text_frames(chromakey_image, last_image)
    frames = background_frames + text_frames
    frames = list(map(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2RGB), frames))
    render_gif(frames, 5, 60)


if __name__ == '__main__':
    font_path = "fonts/VastShadow-Regular.ttf"
    create_subscription_gif("Bandar", "fonts/VastShadow-Regular.ttf", (800, 255))
