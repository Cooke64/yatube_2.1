import os
import secrets

from PIL import Image

from app import app


def save_pic(form_pic):
    # Функция для сохранения фотографии
    random = secrets.token_hex(10)
    _, file_extention = os.path.splitext(form_pic.filename)
    pic_file_name = random + file_extention
    pic_path = os.path.join(
        app.root_path, 'static/profile_pics', pic_file_name)
    # Сохраняем фото в определенном размере
    pic_size = (400, 400)
    image = Image.open(form_pic)
    image.thumbnail(pic_size)
    image.save(pic_path)

    return pic_file_name
