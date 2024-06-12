from PIL import Image, ImageDraw, ImageFont
import os
from ..config import resource_path, cache_path
import datetime

def generate_image(text: str, 
                   title: str = "",  # 标题
                   description: str = "",  # 描述
                   width: int = 600, 
                   min_height: int = 500,
                   background_color: tuple = (255, 255, 255), 
                   text_color: tuple = (0, 0, 0), 
                   title_color: tuple = (0, 0, 0),  # 标题颜色
                   description_color: tuple = (128, 128, 128),  # 描述颜色
                   watermark: str = "fengwind-bot 插件 to_image 1.1",  # 自定义水印文字
                   watermark_font_size: int = 12,  # 水印文字大小
                   font_path = resource_path / 'to_image' / '汉仪润圆-65W.ttf',
                   font_size: int = 24,
                   title_font_size: int = 40,  # 标题文字大小
                   description_font_size: int = 18) -> str:
    """
    生成包含给定文本、标题和描述的图片。

    :param text: 需要转换为图片的文本
    :param title: 标题文本
    :param description: 描述文本
    :param width: 图片的宽度
    :param min_height: 图片的最小高度
    :param background_color: 图片背景颜色
    :param text_color: 文字颜色
    :param title_color: 标题颜色
    :param description_color: 描述颜色
    :param font_path: 字体路径
    :param font_size: 文字字体大小
    :param title_font_size: 标题字体大小
    :param description_font_size: 描述字体大小
    :param watermark: 水印文字
    :param watermark_font_size: 水印文字大小
    :return: 图片文件的路径
    """

    # 创建图像对象
    font = ImageFont.truetype(font_path, font_size)
    title_font = ImageFont.truetype(font_path, title_font_size)
    description_font = ImageFont.truetype(font_path, description_font_size)
    watermark_font = ImageFont.truetype(font_path, watermark_font_size)
    margin = 40  # 边缘间隔设置为20px
    max_width = width - 2 * margin
    
    # 将文本按换行符分割成段落
    paragraphs = text.split('\n')
    lines = []
    
    for paragraph in paragraphs:
        words = paragraph.split()
        while words:
            line = ''
            while words and ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line.strip())
        lines.append('')  # 段落之间添加空行
    
    # 计算文字块高度
    line_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), 'A', font=font)[3]
    text_height = len(lines) * line_height
    title_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), title, font=title_font)[3] if title else 0
    description_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), description, font=description_font)[3] if description else 0
    watermark_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), watermark, font=watermark_font)[3]
    height = max(min_height, text_height + 2 * margin + title_height + description_height + watermark_height + 20)  # 额外添加10px间隔用于标题、描述和水印

    # 创建图像对象
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 计算垂直居中位置
    y = margin

    # 绘制标题
    if title:
        draw.text((margin, y), title, fill=title_color, font=title_font)
        y += title_height + 10  # 标题和描述之间添加10px间隔

    # 绘制描述
    if description:
        draw.text((margin, y), description, fill=description_color, font=description_font)
        y += description_height + 10  # 描述和正文之间添加10px间隔

    # 绘制每一行文字
    for line in lines:
        if line:  # 如果不是空行
            draw.text((margin, y), line, fill=text_color, font=font)
        y += line_height

    # 绘制水印
    draw.text((margin, height - margin - watermark_height), watermark, fill=text_color, font=watermark_font)

    # 保存图片
    name = str(datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S") + ".png")

    # 设置保存图片的路径
    image_path = cache_path / 'to_image'

    # 确保保存路径的文件夹存在
    if not image_path.exists():
        os.makedirs(image_path)

    # 完整的文件路径
    file_path = image_path / name

    # 保存图片
    image.save(file_path)
    image_path = str(file_path)
    return image_path
