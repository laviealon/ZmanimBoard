from typing import List, Dict, Union, Tuple
from datetime import date, time, datetime, timedelta
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar, JewishDate
from pyluach import parshios, dates

GEO_LOCATION = GeoLocation("Hendon", 51.589080, -0.213700, "GMT")
SHACHARIS = "שחרית"
CANDLE_LIGHTING = "הדלקת נרות"
MINCHA_KAB_SHAB = "מנחה וקבלת שבת"
SOF_ZMAN_KSH = "סזק\"ש"
SOF_ZMAN_TEFILLA = "סז\"ת"
MINCHA1 = "מנחה א"
MINCHA2 = "מנחה ב"
MAARIV_MOTZEI = "מעריב ומוצאי שבת"


def rosh_chodesh_name(j: JewishCalendar) -> str:
    """
    Precondition:
        - <j> is a rosh chodesh
    """
    if j.jewish_day == 30:
        month_name = JewishDate(j.jewish_year, j.jewish_month + 1, 1).jewish_month_name()
        if month_name.lower() == "adar_ii":
            month_name = "Adar II"
        return "Rosh Chodesh " + month_name[0].upper() + month_name[1:]
    elif j.jewish_day == 1:
        month_name = j.jewish_month_name()
        if month_name.lower() == "adar_ii":
            month_name = "Adar II"
        return "Rosh Chodesh " + month_name[0].upper() + month_name[1:]


def get_upcoming_significant_days(date: date) -> List[Dict[str, str]]:
    """Return all the upcoming holidays a month from Gregorian date <date>."""
    significant_days = []
    for i in range(30):
        curr_date = date + timedelta(days=i)
        j = JewishCalendar(curr_date)
        if j.significant_day() is not None:
            significant_days.append({j.significant_day(): curr_date.strftime("%b %d")})
        elif j.is_rosh_chodesh():
            significant_days.append({rosh_chodesh_name(j): curr_date.strftime("%b %d")})
    return significant_days


def round_time_up(dt: datetime):
    dt += timedelta(minutes=5 - dt.minute % 5)
    return dt


def round_time_down(dt: datetime):
    dt -= timedelta(minutes=dt.minute % 5)
    return dt


def is_tachanun(date: date) -> bool:
    """Check if tachanun is said on <date>."""


def is_significant_day(date: date) -> bool:
    """Check if <date> marks a Jewish holiday (making services differ)."""
    j = JewishCalendar(date)
    return j.significant_day() is not None


def get_zmanim_erev_shabbos(date: date) -> List[Dict[str, str]]:
    """Return all zmanim on erev shabbos <day>.

    Precondition:
        - <day> is an erev shabbos
    """
    zmanim = []
    zmanim_calendar = ZmanimCalendar(geo_location=GEO_LOCATION, date=date)
    if is_significant_day(date):
        zmanim.append(format_zman(SHACHARIS, time(7, 0)))
    else:
        zmanim.append(format_zman(SHACHARIS, time(7, 15)))
    zmanim.append(format_zman(CANDLE_LIGHTING, zmanim_calendar.candle_lighting()))
    zmanim.append(format_zman(MINCHA_KAB_SHAB, round_time_up(zmanim_calendar.candle_lighting())))
    return zmanim


def add_zman(zmanim: Dict[str, str], name: str, zman: Union[datetime, time]):
    zmanim[name] = zman.strftime("%H:%M")


def get_zmanim_assur_bemelacha(date: date) -> Dict[str, str]:
    zmanim = {}
    zmanim_calendar = ZmanimCalendar(geo_location=GEO_LOCATION, date=date)
    add_zman(zmanim, SOF_ZMAN_KSH, zmanim_calendar.sof_zman_shma_gra())
    add_zman(zmanim, SOF_ZMAN_TEFILLA, zmanim_calendar.sof_zman_tfila_gra())
    add_zman(zmanim, SHACHARIS, time(9, 30))
    add_zman(zmanim, MINCHA1, zmanim_calendar.mincha_gedola())
    add_zman(zmanim, MINCHA2, round_time_down(zmanim_calendar.shkia() - timedelta(minutes=20)))
    add_zman(zmanim, MAARIV_MOTZEI, zmanim_calendar.tzais())
    return zmanim


def get_zmanim_shabbos(date: date) -> Dict[str, str]:
    zmanim = []
    zmanim.append({"פרשת השבוע": parshios.getparsha_string(dates.GregorianDate(date.year, date.month, date.day), hebrew=True)})
    zmanim.extend(get_zmanim_assur_bemelacha(date))
    return zmanim


def get_zmanim_sunday(date: date) -> List[Dict[str, str]]:
    pass


def get_zmanim_weekday(date: date) -> List[Dict[str, str]]:
    pass


def get_zmanim_significant_day(date: date) -> List[Dict[str, str]]:
    pass


if __name__ == '__main__':
    print(get_zmanim_shabbos(date(2022, 3, 5)))
    print(get_upcoming_significant_days(date(2022, 3, 3)))
