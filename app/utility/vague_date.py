import calendar
import re
from datetime import datetime
from enum import Enum
from typing import TypedDict


class DatePrecision(int, Enum):
    WHOLE_DAY = 1
    WHOLE_MONTH = 2
    WHOLE_YEAR = 3
    PART_DAY_MONTH = 4
    PART_DAY = 5
    PART_MONTH = 6


class VagueDate:

    class Value(TypedDict):
        start: datetime
        end: datetime
        type: str

    """
    List of supported date types.
    """
    date_types = [
        # Day-month-year
        'D',
        # Day-month-year range
        'DD',
        # Month-year
        'O',
        # Month-year range
        'OO',
        # Year
        'Y',
        # Year range
        'YY',
        # To year
        '-Y',
    ]

    """
    Lists of regex strings used to try to identify date formats.
    """
    iso8601_regexes = [
        # Day, e.g. yyyy-mm-dd
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),
        # Month, e.g. yyyy-mm
        re.compile(r"^\d{4}-\d{2}$")
    ]

    iso8601_range_regexes = [
        # Day, e.g. yyyy-mm-dd - yyyy-mm-dd
        re.compile(r"""
            ^
            (?P<before>\d{4}-\d{2}-\d{2})
            (?P<sep>\ -\ )  # Spaces have to be escaped when using verbose.
            (?P<after>\d{4}-\d{2}-\d{2})
            $
            """, re.VERBOSE),
        # Month, e.g. yyyy-mm - yyyy-mm
        re.compile(r"""
            ^
            (?P<before>\d{4}-\d{2})
            (?P<sep>\ -\ )
            (?P<after>\d{4}-\d{2})
            $
            """, re.VERBOSE)
    ]

    range_regexes = [
        # Date range, e.g. "d-d/m/yy"
        re.compile(r"""
            (?P<before>.+)
            (?P<sep>-)
            (?P<after>.+)
            """, re.VERBOSE),
        # Range with no start, e.g. "-yyyy"
        re.compile(r"""
            ^
            (?P<sep>-)
            (?P<after>.+)
            """, re.VERBOSE)
    ]

    """
    Arrays of formats used to parse strings with the strptime() function. See
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    whole_day_formats = [
        # 1997-10-12.
        '%Y-%m-%d',
        # 12/10/1997.
        '%d/%m/%Y',
        # 12/10/97.
        '%d/%m/%y',
        # 12.10.1997.
        '%d.%m.%Y',
        # 12.10.97.
        '%d.%m.%y',
        # 12 October 1997.
        '%d %B %Y',
        # 12 Oct 1997.
        '%d %b %Y',
        # 12 October 97.
        '%d %B %y',
        # 12 Oct 97.
        '%d %b %y'
    ]

    partial_day_month_formats = [
        # 10-12.
        '%m-%d',
        # 12/10.
        '%d/%m',
        # 12.10.
        '%d.%m',
        # 12 October.
        '%d %B',
        # 12 Oct.
        '%d %b'
    ]

    partial_day_formats = [
        # 12.
        '%d'
    ]

    whole_month_formats = [
        # 1998-06
        '%Y-%m',
        # 06/1998
        '%m/%Y',
        # 06/96
        '%m/%y',
        # 06.1998
        '%m.%Y',
        # 06.96
        '%m.%y',
        # June 1998
        '%B %Y',
        # Jun 1998
        '%b %Y',
        # June 98
        '%B %y',
        # Jun 98
        '%b %y'
    ]

    partial_month_formats = [
        # 06
        '%m',
        # June
        '%B',
        # Jun.
        '%b'
    ]

    year_formats = [
        # 1998
        '%Y',
        # 98
        '%y'
    ]

    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        start = self._value['start']
        end = self._value['end']
        match self._value['type']:
            case 'D':
                return start.strftime('%d/%m/%Y')
            case 'DD':
                return f"{start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}"
            case 'O':
                return start.strftime('%m/%Y')
            case 'OO':
                return f"{start.strftime('%m/%Y')} - {end.strftime('%m/%Y')}"
            case 'Y':
                return start.strftime('%Y')
            case 'YY':
                return f"{start.strftime('%Y')} - {end.strftime('%Y')}"
            case '-Y':
                return f"- {end.strftime('%Y')}"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, string):
        """Sets a vague date from a string"""

        single_date = None
        start_date = None
        end_date = None
        end_precision = None

        # 1. Determine whether the string is an ISO 8601 date and, if not,
        # whether it is a date range.
        # Have to treat ISO 8601 dates as a special case as they use the
        # hyphen to separate parts which is also our range separator.
        for regex in self.iso8601_regexes:
            match = regex.match(string)
            if match:
                single_date = True
                break

        if single_date is None:
            for regex in self.iso8601_range_regexes:
                match = regex.match(string)
                if match:
                    start = match['before'].strip()
                    end = match['after'].strip()
                    single_date = False
                    break

        if single_date is None:
            for regex in self.range_regexes:
                match = regex.match(string)
                if match:
                    start = match['before'].strip()
                    end = match['after'].strip()
                    single_date = False
                    break

        # Assume a single date if no pattern is matched.
        single_date = True if single_date is None else single_date

        # 2. Extract a date and precision either from
        # the end date if a range else
        # the whole string if not a range
        # Use end_date because this contains more info, e.g. 15-18 Aug 2008
        date_part = string if single_date else end
        whole_formats = {
            DatePrecision.WHOLE_DAY: self.whole_day_formats,
            DatePrecision.WHOLE_MONTH: self.whole_month_formats,
            DatePrecision.WHOLE_YEAR: self.year_formats
        }
        end_date, end_precision = self.parse_date(date_part, whole_formats)

        # 3. Determine the type from the

        if end_precision == DatePrecision.WHOLE_DAY:
            if single_date:
                # Type is D.
                self._value = {
                    'start': end_date,
                    'end': end_date,
                    'type': 'D',
                }
            else:
                # Type is DD.
                day_formats = {
                    DatePrecision.WHOLE_DAY: self.whole_day_formats,
                    DatePrecision.PART_DAY_MONTH: self.partial_day_month_formats,
                    DatePrecision.PART_DAY: self.partial_day_formats
                }
                start_date, start_precision = self.parse_date(
                    start,
                    day_formats
                )
                # Copy across any data not set in the start date.
                if start_precision == DatePrecision.PART_DAY_MONTH:
                    start_date = start_date.replace(year=end_date.year)
                elif start_precision == DatePrecision.PART_DAY:
                    start_date = start_date.replace(year=end_date.year,
                                                    month=end_date.month)
                if start_date < end_date:
                    self._value = {
                        'start': start_date,
                        'end': end_date,
                        'type': 'DD'
                    }
                else:
                    raise ValueError("Invalid date range. Start date must be "
                                     "before end date.")

        elif end_precision == DatePrecision.WHOLE_MONTH:
            # Vague date must start on the first day and end on the last day of
            # the month.
            last_day = calendar.monthrange(end_date.year, end_date.month)[1]

            if single_date:
                # Type is O.
                self._value = {
                    'start': end_date,
                    'end': end_date.replace(day=last_day),
                    'type': 'O'
                }
            else:
                # Type is OO.
                # Find start date and precision.
                month_formats = {
                    DatePrecision.WHOLE_MONTH: self.whole_month_formats,
                    DatePrecision.PART_MONTH: self.partial_month_formats
                }
                start_date, start_precision = self.parse_date(
                    start,
                    month_formats
                )
                # Copy across year if not set in the start date.
                if start_precision == DatePrecision.PART_MONTH:
                    start_date = start_date.replace(year=end_date.year)
                # Fix the end date to the last day of the month.
                end_date = end_date.replace(day=last_day)

                if start_date < end_date:
                    self._value = {
                        'start': start_date,
                        'end': end_date,
                        'type': 'OO'
                    }
                else:
                    raise ValueError("Invalid date range. Start date must be "
                                     "before end date.")

        elif end_precision == DatePrecision.WHOLE_YEAR:
            # Year precision.
            # Vague date must start on the first day and end on the last day of
            # the year.

            if single_date:
                # Type is Y.
                self._value = {
                    'start': end_date,
                    'end': end_date.replace(month=12, day=31),
                    'type': 'Y',
                }
            else:
                if start:
                    # Type is YY.
                    # Find start year.
                    start_date, start_precision = self.parse_date(
                        start,
                        {DatePrecision.WHOLE_YEAR: self.year_formats}
                    )
                    # Fix the end date to the last day of the year.
                    end_date = end_date.replace(month=12, day=31)

                    if start_date < end_date:
                        self._value = {
                            'start': start_date,
                            'end': end_date,
                            'type': 'YY',
                        }
                    else:
                        raise ValueError("Invalid date range. Start date must "
                                         "be before end date.")
                else:
                    # Type is -Y.
                    self._value = {
                        'start': None,
                        'end': end_date,
                        'type': '-Y',
                    }
        else:
            raise ValueError('Unreocognised date format.')

        # A final check that the date is in the past.
        if self._value['end'] > datetime.now():
            raise ValueError('Date is in the future.')

    def parse_date(self, string: str, parse_formats: dict):
        """
        Parses a single date from a string.
        """
        parsed_date = None

        for precision, formats in parse_formats.items():
            for format in formats:
                try:
                    parsed_date = datetime.strptime(string, format)
                    return (parsed_date, precision)
                except ValueError:
                    pass

        if not parsed_date:
            raise ValueError('Unreocognised date format.')
