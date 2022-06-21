"""
I/O routines for handling MiniCyclop data
"""

from astropy.io import ascii
from astropy.time import Time


def read_latest(filename):
    """
    Read the one-line data table that the MiniCyclop outputs with the latest valid data.
    It's a |-delimited ascii table containing the measurement time in 3 different formats
    (UT and MST strings; JD as a float), the zenith-corrected seeing, and the r0 turbulence
    scale factor.

    Parameters
    ----------
    filename: str or Path
        Filename containing latest seeing data

    Returns
    -------
    dict
        Contents include:
            'obstime' : Observation time in `~astropy.time.Time` format
            'obstime_str' : UTC observation time as a ISO-8601 string
            'seeing' : Zenith-corrected seeing in arcsec
            'r0' : Turbulence scale factor in mm
    """
    dt = ascii.read(filename, delimiter='|', names=['UT', 'MST', 'JD', 'flux', 'seeing', 'r0'])
    obstime = Time(dt['JD'][0], scale='utc', format='jd')
    return {
        'obstime': obstime,
        'obstime_str': obstime.isot,
        'seeing': dt['seeing'][0],
        'r0': dt['r0'][0]
    }