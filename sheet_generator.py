from typing import Dict
from datetime import date, timedelta
import zmanim_calculator_winter as zc

DAY = "יום "
SUNDAY = "א\'"
MONDAY = "ב\'"
TUESDAY = "ג\'"
WEDNESDAY = "ד\'"
THURSDAY = "ה\'"
DAY_NAME_LIST = [SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY]
FRIDAY = "ערב שבת"
SHABBOS = "שבת קודש"


def get_week_zmanim_start_sunday(date: date) -> Dict[str, Dict[str, str]]:
    """

    Precondition:
        - <date> is a Sunday
    """
    week_zmanim = {DAY + SUNDAY: zc.get_zmanim_sunday(date) | {"english_name": "Sun"}}
    for i in range(1, 5):
        curr_date = date + timedelta(days=i)
        week_zmanim[DAY + DAY_NAME_LIST[i]] = zc.get_zmanim_weekday(date + timedelta(days=i)) | {"english_name": curr_date.strftime("%a")}
    week_zmanim[FRIDAY] = zc.get_zmanim_erev_shabbos(date + timedelta(days=5))
    week_zmanim[SHABBOS] = zc.get_zmanim_shabbos(date + timedelta(days=6))
    return week_zmanim


# def get_week_zmanim_start_sunday_efficient(date: date) -> Dict[str, Dict[str, str]]:
#     """
#
#     Precondition:
#         - <date> is a Sunday
#     """
#     week_zmanim = {DAY + SUNDAY: zc.get_zmanim_sunday(date)}
#     increment = 1
#     while zc.is_altered_services(date + timedelta(days=increment+1)) \
#             and increment <= 4:
#         week_zmanim[DAY + DAY_NAME_LIST[increment]] = zc.get_zmanim_weekday(date)
#         increment += 1
#     day_string = DAY + DAY_NAME_LIST[increment]
#     for i in range(increment, 5):
#         next_date = date + timedelta(days=i+1)
#         curr_date = date + timedelta(days=i)
#         if zc.is_altered_services(next_date) or next_date.strftime('%A') == 'Friday':
#             day_string += '-' + DAY_NAME_LIST[i]
#             week_zmanim[day_string] = zc.get_zmanim_weekday(curr_date)
#             increment = i
#             break
#         else:
#             continue
#     while zc.is_altered_services(date + timedelta(days=increment+1)) \
#             and increment <= 4:
#         week_zmanim[DAY + DAY_NAME_LIST[increment]] = zc.get_zmanim_weekday(date)
#         increment += 1
#     day_string = DAY + DAY_NAME_LIST[increment]
#     for i in range(increment, 5):
#         next_date = date + timedelta(days=i+1)
#         if zc.is_altered_services(next_date) or next_date.strftime('%A') == 'Friday':
#             day_string += '-' + DAY_NAME_LIST[i]
#             week_zmanim[day_string] = zc.get_zmanim_weekday(date + timedelta(days=i))
#             break
#         else:
#             continue
#     week_zmanim[FRIDAY] = zc.get_zmanim_erev_shabbos(date + timedelta(days=5))
#     week_zmanim[SHABBOS] = zc.get_zmanim_shabbos(date + timedelta(days=6))
#     return week_zmanim


if __name__ == '__main__':
    print(get_week_zmanim_start_sunday(date(2022, 2, 27)))
