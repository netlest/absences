
import io
from flask import Blueprint, Response, current_app
from ..image import AbsMonth
from ..legend import Legend

"""
This blueprint is generating month images
"""

def find_absence_day(absences, day):
    for absence in absences:
        abs_day = absence['abs_date'].day
        if day == abs_day:
            return absence[0]
    return None


bp = Blueprint("month", __name__)

@bp.route('/month/<int:year>/<int:month>')
@bp.route('/month')
def month(year = None, month = None):
  month = AbsMonth(current_app.config, year, month)
  buffer = io.BytesIO()
  img = month.get_image()
  img.save(buffer, 'PNG')
  return Response(buffer.getvalue(), mimetype='image/png')

@bp.route('/legend')
def legend():
  legend = Legend(current_app.config)
  buffer = io.BytesIO()
  img = legend.get_image()
  img.save(buffer, 'PNG')
  return Response(buffer.getvalue(), mimetype='image/png')


@bp.route('/debugimage')
def debugimage():
  month = AbsMonth(current_app.config)
  return month.holiday_caption
