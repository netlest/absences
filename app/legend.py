import os
import random
from PIL import Image, ImageDraw, ImageFont
from .extensions import db
from .models import AbsenceType

class Legend:
  def __init__(self, app_conf):
    self.app_conf = app_conf
    self.padding = 5
    self.img_color = (192, 176, 192)
    self.ttf =  os.path.join(self.app_conf['ROOT_PATH'], "static/ttf","FiraCode-Regular.ttf")
    self.font = ImageFont.truetype(self.ttf, 13)
    self.elements = self.get_elements()
    self.elements_details = self.get_elements_details()
    self.img_width = self.calculate_width()
    self.img_height = 30
    self.img_size = (self.img_width, self.img_height)
    self.image = Image.new("RGB", self.img_size, self.img_color)
    self.draw = ImageDraw.Draw(self.image)
    self.generate_image()

  def get_image(self):
    return self.image

  def generate_random_color(self):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)

  def get_elements(self):
    elements = db.session.query(AbsenceType).order_by(AbsenceType.id).all()
    return elements

  def get_elements_details(self):
    boxes = []
    temp_img = Image.new("RGB", (1, 1), self.img_color)
    temp_draw = ImageDraw.Draw(temp_img)
    
    boxes.append({
      'caption': 'Legend:',
      'text_width': temp_draw.textlength('Legend', font=self.font),
    })

    for element in self.elements:
      caption = element.name
      background = element.color
      text_width = temp_draw.textlength(caption, font=self.font)
      boxes.append({
        'caption': caption,
        'text_width': text_width,
        'background': background
      })
    return boxes

  def calculate_width(self):
    width = self.padding
    for self.element in self.elements_details:
      width += self.element['text_width']+3*self.padding
    return int(width)

  def generate_image(self):
    x1 = self.padding
    y1 = self.padding
    x2 = 0
    y2 = self.img_height-self.padding
    text_v_align = self.img_height/4

    for element in self.elements_details:
      x2 = x1 + element['text_width']+2*self.padding
      if element['caption'] == 'Legend:':
        self.draw.text((x1, text_v_align), element['caption'], font=self.font, fill='#000000')
      else:
        self.draw.rectangle((x1, y1, x2, y2), fill=element.get('background', '#FFFFFF'))
        self.draw.text((x1+self.padding, text_v_align), element['caption'], font=self.font, fill='#000000')
      x1 = x2+self.padding

    return self.image

