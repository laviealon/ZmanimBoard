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
MINCHA_MAARIV = "מנחה ומעריב"
MAARIV = "מעריב"


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


def round_time_up(dt: datetime) -> datetime:
    dt += timedelta(minutes=5 - dt.minute % 5)
    return dt


def round_time_down(dt: datetime) -> datetime:
    dt -= timedelta(minutes=dt.minute % 5)
    return dt


def round_time_nearest(dt: datetime) -> datetime:
    if round(dt.minute / 5) * 5 > dt.minute:
        return round_time_up(dt)
    else:
        return round_time_down(dt)


def is_chol_longer_services(date: date) -> bool:
    """Check if there are longer services on this chol day (Hallel, Musaf,
    Torah reading).

    Precondition:
        - <date> is a chol date (melacha is permitted), not including Purim, Tisha B'av,
        Aseres Yemei Teshuva, and days on which selichos are said
        (all these have their own functions)
    """
    j = JewishCalendar(date)
    return j.significant_day() in ["chol_hamoed_succos", "hoshana_rabbah", "chanukah",
                                   "tenth_of_teves", "taanis_esther", "chol_hamoed_pesach",
                                   "seventeen_of_tammuz"] or j.is_rosh_chodesh()


def is_kodesh_or_misc(date: date):
    """Check if weekday corresponds to:
        (A) kodesh: shalosh regalim, shemini atzeres/simchas torah,
        rosh hashana, yom kippur
        (B) misc: tisha b'av, purim, tzom gedalia, selichos,
        aseres yemei teshuva, or erev kodesh

    Precondition:
        - <date> is a weekday
    """
    j = JewishCalendar(date)
    is_kodesh = j.significant_day() in ['pesach', 'succos', 'shavuos',
                                        'shemini_atzeres', 'simchas_torah',
                                        'rosh_hashana', 'yom kippur']
    is_misc = j.significant_day() in ['purim']
    return is_kodesh or is_misc


def is_altered_services(date: date):
    """Return if weekday corresponds to altered services."""
    return is_chol_longer_services(date) or is_kodesh_or_misc(date)


def is_significant_day(date: date) -> bool:
    """Check if <date> marks a Jewish significant day of any kind."""
    j = JewishCalendar(date)
    return j.significant_day() is not None


def get_zmanim_erev_shabbos(date: date) -> Dict[str, str]:
    """Return all zmanim on erev shabbos <day>.

    Precondition:
        - <day> is an erev shabbos
    """
    zmanim = {}
    zmanim_calendar = ZmanimCalendar(geo_location=GEO_LOCATION, date=date)
    if is_significant_day(date):
        add_zman(zmanim, SHACHARIS, time(7, 0))
    else:
        add_zman(zmanim, SHACHARIS, time(7, 15))
    add_zman(zmanim, CANDLE_LIGHTING, zmanim_calendar.candle_lighting())
    add_zman(zmanim, MINCHA_KAB_SHAB, round_time_up(zmanim_calendar.candle_lighting()))
    return zmanim


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
    parsha = {"פרשת השבוע": parshios.getparsha_string(
        dates.GregorianDate(date.year, date.month, date.day), hebrew=True)}
    return parsha | get_zmanim_assur_bemelacha(date)


def get_zmanim_sunday(date: date) -> Dict[str, str]:
    zmanim = {}
    zmanim_calendar = ZmanimCalendar(geo_location=GEO_LOCATION, date=date)
    add_zman(zmanim, SHACHARIS, time(9, 00))
    add_zman(zmanim, MINCHA_MAARIV, round_time_nearest(zmanim_calendar.shkia() - timedelta(minutes=10)))
    add_zman(zmanim, MAARIV, time(19, 0))
    return zmanim


def redirect_kodesh_or_misc(date: date) -> Dict[str, str]:
    pass


def get_zmanim_weekday(date: date) -> Dict[str, str]:
    zmanim = {}
    if is_chol_longer_services(date):
        add_zman(zmanim, SHACHARIS, time(7, 00))
    elif is_kodesh_or_misc(date):
        return redirect_kodesh_or_misc(date)
    else:
        add_zman(zmanim, SHACHARIS, time(7, 15))
    add_zman(zmanim, MAARIV, time(19, 00))
    return zmanim


def get_zmanim_significant_day(date: date) -> List[Dict[str, str]]:
    pass


def add_zman(zmanim: Dict[str, str], name: str, zman: Union[datetime, time]):
    zmanim[name] = zman.strftime("%H:%M")


if __name__ == '__main__':
    print(get_zmanim_shabbos(date(2022, 3, 5)))
    print(get_upcoming_significant_days(date(2022, 3, 3)))
    print(get_zmanim_sunday(date(2022, 2, 27)))
