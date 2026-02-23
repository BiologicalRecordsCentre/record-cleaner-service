# Date

Dates can be entered in 3 basic formats:

* A single date,
* A date range,
* An open-ended date range.

## Single Dates

Single dates can represent a specific day, month, or year.

The following day formats are accepted. In all cases:

* Leading zeros on single digit days and months are not required unless stated.
* Four-digit years should be used. (Dates with two-digit years will be accepted
and converted to four digits, but this may produce an incorrect year.)

Pattern | Example | Notes
--- | --- | ---
yyyy-mm-dd | 2024-03-07 | A leading 0 is required on single digit days and months.
d/m/yyyy | 7/3/2024 or 07/03/2024 | 
d.m.yyyy | 7.3.2024 or 07.03.2024 |
d month yyyy | 7 March 2024 or 07 March 2024 |
d mon yyyy | 7 Mar 2024 or 07 Mar 2024 |

Month formats are the same as above but with the day omitted. E.g. 3/2024

A single year can also be used. E.g. 2024

## Date Ranges
Date ranges consist of a start date and an end date separated by a hyphen. They 
can represent specific day, month or year ranges.

The following day-range formats are accepted. In all cases:

* The end date should be in one of the formats accepted for single dates.
* Space around the hyphen is not required unless stated.
* The start date can be abbreviated, unless stated otherwise, by omitting year 
and month if they are the same as for the end date.

Pattern | Example | Notes
--- | --- | ---
yyyy-mm-dd - yyyy-mm-dd | 2024-03-07 - 2024-03-09 | A space is required each side of the central hyphen. Month and year cannot be omitted from the start date.
d-d/m/yyyy | 7-9/3/2024 or 07-09/03/2024 | 
d/m-d/m/yyyy | 7/2-9/3/2024 or 07/02-09/03/2024 | 
d/m/yyyy-d/m/yyyy | 7/3/2024-9/3/2024 or 07/03/2024-09/03/2024 |


Similarly, the following month ranges are accepted.

Pattern | Example | Notes
--- | --- | ---
yyyy-mm - yyyy-mm | 2024-02 - 2024-03 | A space is required each side of the central hyphen. Year cannot be omitted from the start date.
m-m/yyyy | 2-3/2024 or 02-03/2024 | 
m/yyyy-m/yyyy | 2/2024-3/2024 or 02/2024-03/2024 |

A year range is simply yyyy - yyyy, E.g. 2022 - 2023

## Open-ended Date Ranges

A single open-ended format is supported, `-yyyy`, e.g. -2023, meaning up to and including the given year. An open end-date format is no longer supported because
you are not presumed to have the power of predicting the future.