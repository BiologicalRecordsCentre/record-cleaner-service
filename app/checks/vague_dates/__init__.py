import datetime
import re
from typing import TypedDict




class VagueDate:

    class Value(TypedDict):
        start: datetime.datetime 
        end: datetime.datetime    
        type: str
    
    _value = Value({
        'start': None,
        'end': None,
        'type': None
    })
    

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
    List of regex strings used to try to capture date ranges.

    The 'regex' key should, naturally, point to the regular expression. 'start'
    should point to the backreference for the string to be parsed for the
    'start' date, 'end' to the backreference of the string to be parsed for
    the 'end' date. -1 means grab the text before the match, 1 means after, 0
    means set the value to empty. Types are not determined here. Should either
    'start' or 'end' contain the string '...', this will be interpreted as
    one-ended range.
    """
    date_range_strings = [
        {
            # Any range with space around hyphen, e.g. "anything - anything"
            'regex': re.compile(r'(?P<sep> - )'),
            'start': -1,
            'end': 1,
        },
        {
            # Date range, e.g. "dd/mm/yyyy-dd/mm/yyyy"
            'regex': re.compile(r'^\d{2}[\/\.]\d{2}[\/\.]\d{2}(\d{2})?(?P<sep>-)\d{2}[\/\.]\d{2}[\/\.]\d{2}(\d{2})?$'),
            'start': -1,
            'end': 1,
        },
        {
            # Month in year range, e.g. "mm/yyyy-mm/yyyy"
            'regex': re.compile(r'^\d{2}[\/\.]\d{2}(\d{2})?(?P<sep>-)\d{2}[\/\.]\d{2}(\d{2})?$'),
            'start': -1,
            'end': 1,
        },
        {
            # Year range, e.g. "yyyy-yyyy"
            'regex': re.compile(r'^\d{4}(?P<sep>-)\d{4}$'),
            'start': -1,
            'end': 1,
        },
        {
            # To year, e.g. "-yyyy"
            'regex': re.compile(r'^(?P<sep>-)'),
            'start': 0,
            'end': 1,
        },
    ]

    """
    Array of formats used to parse a string looking for a single day with the
    strptime() function. See
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    single_day_formats = [
        # ISO 8601 date format 1997-10-12.
        '%Y-%m-%d',
        # 12/10/1997.
        '%d/%m/%Y',
        # 12/10/97.
        '%d/%m/%y',
        # 12.10.1997.
        '%d.%m.%Y',
        # 12.10.97.
        '%d.%m.%y',
        # Monday 12 October 1997.
        '%A %e %B %Y',
        # Mon 12 October 1997.
        '%a %e %B %Y',
        # Monday 12 Oct 1997.
        '%A %e %b %Y',
        # Mon 12 Oct 1997.
        '%a %e %b %Y',
        # Monday 12 October 97.
        '%A %e %B %y',
        # Mon 12 October 97.
        '%a %e %B %y',
        # Mon 12 Oct 97.
        '%a %e %b %y',
        # Monday 12 Oct 97.
        '%A %e %b %y',
        # Mon 12 Oct 97.
        '%a %e %b %y',
        # Monday 12 October.
        '%A %e %B',
        # Mon 12 October.
        '%a %e %B',
        # Monday 12 Oct.
        '%A %e %b',
        # Mon 12 Oct.
        '%a %e %b',
        # 12 October 1997.
        '%e %B %Y',
        # 12 Oct 1997.
        '%e %b %Y',
        # 12 October 97.
        '%e %B %y',
        # 12 Oct 97.
        '%e %b %y',
        # American date format.
        '%m/%d/%y',
    ]

    """
    Array of formats used to parse a string looking for a single month in a 
    year with the strptime() function. See 
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    single_month_in_year_formats = [
        # ISO 8601 format - truncated to month 1998-06
        '%Y-%m',
        # 06/1998
        '%m/%Y',
        # 06/96
        '%m/%y',
        # June 1998
        '%B %Y',
        # Jun 1998
        '%b %Y',
        # June 98
        '%B %y',
        # Jun 98
        '%b %y'
    ]

    single_year_formats = [
        # 1998
        '%Y',
        # 98
        '%y'
    ]




    def __init__(self, value: str):
        self._value = value


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
        return self.value

    @value.setter
    def value(self, v):
        self._value = v

        if isinstance(v, str):
            # Create a vague date from a string.
            self.value = self.string_to_vague_date(v)


 
    def string_to_vague_date(self, string):
        """
        Convert a string into a vague date.

        Args:
            string (str): The date as a string.

        Returns:
            Union[Dict[str, Union[datetime.datetime, str]], bool]: An dictionary with 3 entries, the start date, end date and date type, or
            False if the format can't be matched.
        """
        parseFormats = [
            self.singleDayFormats,
            self.singleMonthInYearFormats,
            self.singleYearFormats
        ]

        # Our approach shall be to gradually pare down from the most complex
        # possible dates to the simplest, and match as fast as possible to try 
        # to grab the most information. First we consider the potential ways 
        # that a range may be represented.
        date_range = False
        start_date = False
        end_date = False
        matched = False

        for a in self.date_range_strings:
            if re.match(a['regex'], string, re.IGNORECASE):
                regs = re.match(a['regex'], string, re.IGNORECASE).groupdict()
                if a['start'] == -1:
                    start = string[:string.index(regs['sep'])].strip()
                elif a['start'] == 1:
                    start = string[string.index(regs['sep']) + len(regs['sep']):].strip()
                else:
                    start = False

                if a['end'] == -1:
                    end = string[:string.index(regs['sep'])].strip()
                elif a['end'] == 1:
                    end = string[string.index(regs['sep']) + len(regs['sep']):].strip()
                else:
                    end = False
                date_range = True
                break

        if not date_range:
    a = self.parse_single_date(string, parseFormats)
    if a:
        startDate, endDate = endDate, a
        matched = True
    else:
        if start:
            a = self.parse_single_date(start, parseFormats)
            if a is not None:
                startDate, matched = a, True
        if end:
            a = self.parse_single_date(end, parseFormats)
            if a is not None:
                endDate, matched = a, True
        if matched and start and not end:
            endDate = startDate
        if matched and end and not start:
            startDate = endDate
    if not matched:
        if string.strip() == 'U' or string.strip() == Kohana.lang('dates.unknown'):
            return [None, None, 'U']
        else:
            return False
    # Okay, now we try to determine the type - we look mostly at endDate because
    # This is more likely to contain more info e.g. 15 - 18 August 2008
    # Seasons are parsed specially - i.e. we'll have seen the word 'Summer'
    # or the like.
    try:

        if endDate.tm_season is not None:
            # We're a season. That means we could be P (if we have a year) or
            # S (if we don't).
            if endDate.tm_year is not None:
                # We're a P.
                vagueDate = [
                    endDate.get_imprecise_date_start(),
                    endDate.get_imprecise_date_end(),
                    'P',
                ]
                return validate(vagueDate)
            else:
                # No year, so we're an S.
                vagueDate = [
                    endDate.get_imprecise_date_start(),
                    endDate.get_imprecise_date_end(),
                    'S',
                ]
                return validate(vagueDate)

        # Do we have day precision?
        if endDate.tm_mday is not None:
            if not date_range:
                # We're a D.
                vagueDate = [
                    endDate.get_iso_date(),
                    endDate.get_iso_date(),
                    'D',
                ]
                return validate(vagueDate)
            else:
                # Type is DD. We copy across any data not set in the
                # start date.
                if startDate.get_precision() == endDate.get_precision():
                    vagueDate = [
                        startDate.get_imprecise_date_start(),
                        endDate.get_imprecise_date_end(),
                        'DD',
                    ]
                else:
                    # Less precision in the start date -
                    # try and massage them together.
                    return False
                return validate(vagueDate)

        # Right, scratch the possibility of days. Months are next. 
        #Months can be:
        # Type 'O' - month, year, !range
        # Type 'OO' - month, year, range

        if endDate.tm_mon is not None:
            if not date_range:
                # Either a month in a year or just a month.
                if endDate.tm_year is not None:
                    # Then we have a month in a year- type O.
                    vagueDate = [
                        endDate.get_imprecise_date_start(),
                        endDate.get_imprecise_date_end(),
                        'O',
                    ]
                    return validate(vagueDate)
                else:
                    # Month without a year - type M.
                    vagueDate = [
                        endDate.get_imprecise_date_start(),
                        endDate.get_imprecise_date_end(),
                        'M',
                    ]
                    return validate(vagueDate)
            else:
                # We do have a range, OO.
                if endDate.tm_year is not None:
                    # We have a year - so this is OO.
                    vagueDate = [
                        startDate.get_imprecise_date_start(),
                        endDate.get_imprecise_date_end(),
                        'OO',
                    ]
                    return validate(vagueDate)
                else:
                    # MM is not an allowed type.
                    # TODO think about this.
                    return False
    """
    No day, no month. We're some kind of year representation - Y,YY, or
    -Y.
    """
    if end_date.tm_year is not None:
        if not date_range:
            # We're Y.
            vague_date = {
                'start': end_date.get_imprecise_date_start(),
                'end': end_date.get_imprecise_date_end(),
                'type': 'Y',
            }
            return validate(vague_date)
        else:
            if start and end:
                # We're YY.
                vague_date = {
                    'start': start_date.get_imprecise_date_start(),
                    'end': end_date.get_imprecise_date_end(),
                    'type': 'YY',
                }
                return validate(vague_date)
            elif end and not start:
                # We're -Y.
                vague_date = {
                    'start': None,
                    'end': end_date.get_imprecise_date_end(),
                    'type': '-Y',
                }
                return validate(vague_date)
    else:
        return False
    except Exception as e:
        return False





















  /**
   * Parses a single date from a string.
   */
  protected static function parseSingleDate($string, $parseFormats) {
    $parsedDate = NULL;

    foreach ($parseFormats as $a) {
      $dp = new DateParser($a);

      if ($dp->strptime($string)) {
        $parsedDate = $dp;
        break;
      }
    }

    return $parsedDate;
  }


  /**
   * Returns true if the supplied date is the first day of the month.
   */
  protected static function is_month_start($date) {
    return ($date->format('j') == 1);
  }

  /**
   * Returns true if the supplied date is the last day of the month.
   */
  protected static function is_month_end($date) {
    // Format t gives us the last day of the given date's month.
    return ($date->format('j') == $date->format('t'));
  }

  }

  /**
   * Returns true if the supplied dates are in the same month.
   */
  protected static function is_same_month($date1, $date2) {
    return ($date1->format('m') == $date2->format('m'));
  }

  /**
   * Returns true if the supplied date is the first day of the year.
   */
  protected static function is_year_start($date) {
    return ($date->format('j') == 1 && $date->format('m') == 1);
  }

  /**
   * Returns true if the supplied date is the last day of the year.
   */
  protected static function is_year_end($date) {
    return ($date->format('j') == 31 && $date->format('m') == 12);
  }

  /**
   * Returns true if the supplied dates are in the same year.
   */
  protected static function is_same_year($date1, $date2) {
    return ($date1->format('Y') == $date2->format('Y'));
  }

  
  

  /**
   * Ensure a vague date array is well-formed.
   */
  protected static function validate($vagueDate) {
    $start = $vagueDate[0];
    $end = $vagueDate[1];
    $type = $vagueDate[2];

    if ($end < $start && !is_null($end)) {
      // End date must be after start date.
      return FALSE;
    }
    else {
      return $vagueDate;
    }
  }

  /**
   * Tests that a check passed, and if not throws an exception containing the
   * message. Replacements in the message can be supplied as additional string
   * parameters, with %s used in the message. The replacements can also be null
   * or datetime objects which are then converted to strings.
   */
  protected static function check($pass, $message) {
    if (!$pass) {
      $args = func_get_args();
      // Any args after the message are string format inputs for the message.
      unset($args[0]);
      unset($args[1]);
      $inputs = [];
      foreach ($args as $arg) {
        kohana::log('debug', 'arg ' . gettype($arg));
        if (gettype($arg) == 'object') {
          $inputs[] = $arg->format(Kohana::lang('dates.format'));
        }
        elseif (gettype($arg) === 'NULL') {
          $inputs[] = 'null';
        }
        else {
          $inputs[] = $arg;
        }
      }
      throw new Exception(vsprintf($message, $inputs));
    }
  }

}
