from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import date, datetime
import os
from flask import session, current_app, url_for
from flask_login import current_user
from sqlalchemy import extract
from .models import Object, User, Group, Holiday, VAbsence, AbsenceType
from .extensions import db

"""
curdate - refers to built month/year if requested, else equals today - date obj
year = integer - refers to year requested, else current year
month = integer - refers to day requested, else current year
day = integer - refers to day requested, else current day
today - date objects always reffering to real current calendar day
"""

def get_key_by_value(d, value):
    return next((k for k, v in d.items() if v == value), None)

class AbsMonth:
  def __init__(self, app_conf, year = None, month = None):
    self.app_conf = app_conf
    self.cal = calendar.Calendar()
    self.today = date.today()

    if year is None:
      self.year = self.today.year
    else:
      self.year = year

    if month is None:
      self.month = self.today.month
    else:
     self.month = month

    if year is not None and month is not None:
      self.curdate = date(year, month, 1)
    else:
      self.curdate = date.today()

    self.objects = self.find_objects()           # Fetch objects from database
    self.absences = self.find_absences()         # Fetch absences from database
    self.object_order = self.sort_objects()      # Store mapping between calendar row and object_id {rowno: object_id}
    self.img_items = len(self.objects)           # Number of rows for calendar so image height depends on number of objects

    self.day = self.curdate.day
    self.monthrange = calendar.monthrange(self.year, self.month)
    self.number_of_days = self.monthrange[1]     # no of days in given month
    self.img_color = (192, 176, 192)
    self.img_row_label_width = 250
    self.img_col_width = 25
    self.img_row_height = 35
    self.img_header_rows = 2
    self.img_font_size = 13
    self.img_width = 1+self.img_row_label_width+31*(self.img_col_width+1)
    self.img_height = (self.img_items+self.img_header_rows)*(self.img_row_height+1)
    self.img_size = (self.img_width, self.img_height)
    self.image = Image.new("RGB", self.img_size, self.img_color)
    self.draw = ImageDraw.Draw(self.image)
    self.ttf =  os.path.join(self.app_conf['ROOT_PATH'], "static/ttf","FiraCode-Regular.ttf")
    self.font = ImageFont.truetype(self.ttf, 13)
    self.font1 = ImageFont.truetype(self.ttf, 20)
    self.cur_month_str = (self.curdate.strftime('%B'))
    self.week_number = self.curdate.strftime('%W')

    self.absences_details = []          # Details of absences with coordinates. Used to build image map
                                        # {object_id, rowno, day, duration, description, color, x1, y1, x2, y2}

    self.holiday_caption = {}           # Details of holiday. Used to build image map {day: description}
    self.img_map = []                   # HTML map for image
    self.generate_image()

  def get_image(self):
    return self.image

  # Fetch objects from database and add them to calendar
  # Store mapping between object and row number
  def find_objects(self):

      group_id = session.get('group_id')
      if group_id is None:
          current_app.logger.error("group_id not found in the session")
          current_app.logger.info(f"Current session content: {session}")


      # Find objects related to the current group
      query = db.session.query(
          Object.id,
          Object.user_id,
          Object.group_id,
          User.username.label('owner'),
          Group.name.label('group_name'),
          Object.name.label('object_name'),
          Object.description
      ).join(Group, Object.group_id == Group.id, isouter=True)\
      .join(User, Object.user_id == User.id, isouter=True)\
      .filter(Group.id == group_id)

      # If SHOW_ALL_GROUP_OBJECTS is False or user is not admin filter only user objects
      if not self.app_conf['SHOW_ALL_GROUP_OBJECTS'] and not current_user.admin :
          query = query.filter(Object.user_id == current_user.id)
  
      objects = query.all()

      # for obj in objects:
      #   current_app.logger.info('Fetched object. ID: %s NAME: %s', obj.id, obj.object_name)

      return objects
  
  # Get absences from database
  def find_absences(self):
    group_id = session.get('group_id')
    if group_id is None:
        current_app.logger.error("group_id not found in the session")
        current_app.logger.info(f"Current session content: {session}")

    query = VAbsence.query.filter(
        extract('month', VAbsence.abs_date_start) == self.month,
        extract('year', VAbsence.abs_date_start) == self.year,
        VAbsence.group_id == group_id
    )

    # If SHOW_ALL_GROUP_OBJECTS is False or user is not admin filter only user objects absences
    if not self.app_conf['SHOW_ALL_GROUP_OBJECTS'] and not current_user.admin :
      query = query.filter(VAbsence.user_id == current_user.id)

    absences = query.all()

    current_app.logger.info('Fetched absences. COUNT: %s', len(absences))
    
    # for absence in absences:
    #   current_app.logger.info('Fetched absence. ID: %s OBJECT_ID: %s GROUP_ID: %s ABS_DATE_START: %s ABS_DATE_END: %s, DURATION: %s',
    #                           absence.id, absence.object_id, absence.group_id, absence.abs_date_start, absence.abs_date_end, absence.duration)
    
    return absences
  
  def find_absence_day(self, absences, day):
    for absence in absences:
        abs_day = absence['abs_date_start'].day
        if day == abs_day:
            return absence[0]
    return None

  # Check if given day is within any of absence periods of given object_id
  # Return related absence object if found, else None
  def check_day(self, day, object_id):
    given_date = date(self.year, self.month, day)
    for absence in self.absences:
      if (absence.object_id == object_id) and (absence.abs_date_start <= given_date <= absence.abs_date_end):
          return absence
    return None

  # Mark holiday on given day in header row
  def mark_holiday(self, day):
    x1=self.img_row_label_width-self.img_col_width+(day*self.img_col_width)+day
    y1=self.img_row_height
    x2=x1+self.img_col_width-1
    y2=y1+self.img_row_height
    self.draw.rectangle((x1,y1,x2,y2),fill='#e121ff')

  # Mark day in given row with given color
  # Offset - how many days to mark from given day
  # Return coordinates of marked area
  def mark_day(self, row, day, color, duration=1, caption=None):
    x1=self.img_row_label_width-self.img_col_width+(day*self.img_col_width)+day
    y1=(row*self.img_row_height)+row
    x2=x1+(self.img_col_width*duration)+duration-2
    y2=y1+self.img_row_height-1
    self.draw.rectangle((x1,y1,x2,y2),fill=color)
    
    # Handle caption
    if caption:
      box_width = x2 - x1
      text_width = self.draw.textlength(caption, font=self.font)
      if text_width > box_width:
        while text_width > box_width and len(caption) > 0:
            caption = caption[:-1]
            text_width = self.draw.textlength(caption, font=self.font)
      self.draw.text((x1, y1+(self.img_row_height/4)), str(caption), font=self.font, fill='#000000')
    
    return x1, y1, x2, y2

  # Get coordinates for given day and row
  def get_coordinates(self, row, day):
    x1=self.img_row_label_width-self.img_col_width+(day*self.img_col_width)+day
    y1=(row*self.img_row_height)+row
    x2=x1+self.img_col_width-1
    y2=y1+self.img_row_height-1
    return x1, y1, x2, y2

  # Generate html image map for calendar image
  def gen_map(self):
    # Loop every row first
    entry = f'<map name="{self.month}{self.year}">'
    self.img_map.append(entry)

    # Loop through absences and add them to map
    for absence in self.absences_details:
      if self.app_conf['MODIFY_ALL_GROUP_ABSENCES'] or absence["user_id"] == current_user.id or current_user.admin:
        entry = (
            f'<area shape="rect" coords="{absence["x1"]},{absence["y1"]},{absence["x2"]},{absence["y2"]}" '
            f'href="{url_for("abs.edit",id=absence["absence_id"])}" '
            f'title="{absence["description"]}">'
        )

        self.img_map.append(entry)


    for row in range(1, self.img_items+2):

      # Check days in header row
      if row == 1:
        for day in range(1, self.number_of_days+1):
          x1, y1, x2, y2 = self.get_coordinates(row, day)

          holiday_title = self.holiday_caption.get(day, None)
          if holiday_title:
            entry = f'<area shape="rect" coords="{x1},{y1},{x2},{y2}" nohref title="{holiday_title}">'
            self.img_map.append(entry)

      # Check days in object rows
      if row >= 2:
          object_id = self.object_order[row]
          obj = next((obj for obj in self.objects if obj.id == object_id), None)
          # current_app.logger.info('Generating map for object %s id: %s rowno: %s', obj.object_name, obj.id, row)
      
          for day in range(1, self.number_of_days+1):
            x1, y1, x2, y2 = self.get_coordinates(row, day)

            if self.check_day(day, object_id) is None:
              if self.app_conf['MODIFY_ALL_GROUP_ABSENCES'] or obj.user_id == current_user.id or current_user.admin:
                  entry = (
                    f'<area shape="rect" coords="{x1},{y1},{x2},{y2}"'
                    f'href="{url_for("abs.create",object_id=object_id,day=day,month=self.month,year=self.year,goback=1)}"'
                    f'title="Add">'
                  )
                  self.img_map.append(entry)
    
    self.img_map.append('</map>')

  # Draw white box around current day
  def mark_curday(self, day):
    x1=self.img_row_label_width-self.img_col_width+(day*self.img_col_width)+day
    y1=self.img_row_height
    x2=x1+self.img_col_width-1
    y2=y1+(self.img_row_height*(self.img_items+1))+self.img_items
    self.draw.rectangle((x1,y1,x2,y2), outline='#ffffff', width=2)

  # Add object name to given row
  def add_object(self, name, row):
    x1 = 5
    y1=(row*self.img_row_height)+row+7
    self.draw.text((x1, y1), str(name), font=self.font, fill='#000000')

  # Mark absences on calendar
  def mark_abs(self):

    for absence in self.absences:
      object_id = absence.object_id
      day = absence.abs_date_start.day
      color = absence.at_color
      duration = absence.duration
      description = absence.description
      rowno = get_key_by_value(self.object_order, absence.object_id)
      
      # current_app.logger.info('Marking absence for objet_id: %s: day: %s,  color: %s,  duration: %s,  description: %s,  rowno: %s', 
      #                         object_id, day, color, duration, description, rowno)
    
      x1, y1, x2, y2 = self.mark_day(rowno, day, color, duration, description)
    
      self.absences_details.append({
        'absence_id': absence.id,
        'object_id': absence.object_id,
        'user_id': absence.user_id,
        'rowno': rowno,
        'day': day,
        'duration': duration,
        'description': description,
        'color': color,
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2          
      })
  
  # Return mapping between row number and object id
  def sort_objects(self):
    idx = 2 # Row two is first row with objects # Row 1 is header # Row 0 CW
    order = {}
    for obj in self.objects:
       order[idx] = obj.id
       idx += 1
    return order
  
  # Draw objects names on calendar rows
  def draw_objects(self):
      for obj in self.objects:
        rowno = get_key_by_value(self.object_order, obj.id)
        # current_app.logger.info('Adding object %s id: %s to row: %s', obj.object_name, obj.id, rowno)
        self.add_object(obj.object_name, rowno)

  # Mark holidays on calendar
  def mark_holidays(self):
      captions = {}

      # Mark recurring holidays
      holidays = db.session.query(Holiday).filter(
          extract('month', Holiday.event_date) == self.month,
          Holiday.recurring == True
      ).all()

      for holiday in holidays:
          self.mark_holiday(holiday.event_date.day)
          captions[holiday.event_date.day] = holiday.description
      
      # Mark fixed date holidays
      holidays = db.session.query(Holiday).filter(
          extract('month', Holiday.event_date) == self.month,
          extract('year', Holiday.event_date) == self.year,
          Holiday.recurring == False
      ).all()

      for holiday in holidays:
          self.mark_holiday(holiday.event_date.day)
          captions[holiday.event_date.day] = holiday.description

      self.holiday_caption = captions
 
 
  # Generate image - main function
  def generate_image(self):

    # Highlight weekends
    cwweekends = []
    for day in self.cal.itermonthdays4(self.year, self.month):
      if(day[1] == self.month):
        if(day[3] == 5):
          if(day[2] + 1 > self.number_of_days):
            end = 1
          else:
            end = 2
          cwweekends.append((day, end))

    for cwweekend in cwweekends:
      first_day = cwweekend[0][2]
      end = cwweekend[1]
      x1 = self.img_row_label_width+(first_day-1)*self.img_col_width+first_day
      y1 = 1
      x2 = x1 + (end * self.img_col_width) + end-2
      y2 = self.img_height-1
      self.draw.rectangle((x1, y1, x2, y2),fill='#A090A0')

    # Draw grid
    for left_margin in range(self.img_row_label_width, self.img_width, self.img_col_width+1):
      self.draw.line((left_margin, 0, left_margin, self.img_height), fill='#808080', width=1)

    for top_margin in range(self.img_header_rows * self.img_row_height + 1, self.img_height, self.img_row_height+1):
      self.draw.line((0, top_margin, self.img_width, top_margin),fill='#808080', width=1)

    # Mark holidays
    self.mark_holidays()

    # Add monthdays
    cur_x=self.img_row_label_width
    for day in range(1, self.number_of_days+1, 1):
      self.draw.text((cur_x+5, self.img_row_height+5), str(day), font=self.font, fill=(0, 0, 0))
      cur_x += 26

    # Add extra padding when days < 31
    padding=31-self.number_of_days
    if(padding>0):
      self.draw.rectangle((self.img_width-self.img_col_width * padding - padding,0,self.img_width, self.img_height),fill='#605060')

    """Build cwperiods array with information about first day of
    week + day code
    how many days left until saturday or end of current month
    and number of current week
    ((yyyy, mm, dd, day_code), days_until_saturday, number of week)"""
    
    cwperiods = []
    idx = 0
    for day in self.cal.itermonthdays4(self.year, self.month):
      if(day[1] == self.month):
        weekno=datetime(day[0], day[1], day[2]).isocalendar().week
        if(day[3] < 5 and idx==0):
          days_until_saturday = 5 - day[3]
          cwperiods.append((day, days_until_saturday, weekno))
        elif(day[3] == 0):
          days_until_saturday = 5
          if(day[2] + days_until_saturday > self.number_of_days):
            days_until_saturday = self.number_of_days+1 - day[2]
          cwperiods.append((day, days_until_saturday, weekno))
        idx += 1

    # Loop through week numbers and draw them on grid
    for cwperiod in cwperiods:
      first_day = cwperiod[0][2]
      end = cwperiod[1]
      weekno = cwperiod[2]
      x1 = self.img_row_label_width+(first_day-1)*self.img_col_width+first_day
      y1 = 1
      x2 = x1 + (end * self.img_col_width) + end-2
      y2 = self.img_row_height-2
      self.draw.rectangle((x1, y1, x2, y2),fill='#ba90ba')
      box_height = y2 - y1
      # there must be at least two days in period to draw week number
      if(end > 1):
        margin = (end*self.img_col_width/2)-(self.img_col_width-5)
        self.draw.text((x1+margin, y1+(box_height/4)), 'CW ' + str(weekno), font=self.font, fill='#000000')

    # Add current month info
    if(self.month == self.today.month and self.year == self.today.year):
      color='#2020FF'
    else:
      color='#000000'
    
    self.draw.text((15, self.img_row_height/2), self.cur_month_str + ' ' + str(self.year), font=self.font1, fill=color)

    # Highlight current month with white 2px box
    if(self.curdate.month == self.today.month):
      self.draw.rectangle((0, 0, self.img_width, self.img_height), outline='#ffffff', width=2)


    self.draw_objects()
    self.mark_abs()

    # Mark current day with white box
    if(self.month == self.today.month and self.year == self.today.year):
      self.mark_curday(self.today.day)

    self.gen_map()

    return self.image

