"""
There is some jitter in the arrival times of packets from the MCU (as
reflected in the sysclock records in the .rec file. If we assume that
the Trodes clock is actually regular, and that any episodes of lag are
fairly sporadic, we can recover the correspondence between trodestime
and system (wall) time.
"""

import numpy as np
import pandas as pd
from rec_to_binaries.create_system_time import infer_systime
from rec_to_binaries.read_binaries import (readTrodesExtractedDataFile,
                                           write_trodes_extracted_datafile)
from scipy.stats import linregress


def _label_time_chunks(trodestime):
    """Labels each consecutive chunk of time with an integer.

    Parameters
    ----------
    trodestime : numpy.ndarray, shape (n_time,)

    Returns
    -------
    time_label : numpy.ndarray, shape (n_time,)
        Labels each consecutive chunk of time with an integer.

    """
    trodestime = np.asarray(trodestime)
    is_gap = np.diff(trodestime) > 1
    is_gap = np.insert(is_gap, 0, False)
    return np.cumsum(is_gap)


def _regress_timestamps(trodestime, systime):
    """Regress the timestamps onto the trodes index

    Parameters
    ----------
    trodestime : array_like, uint32
        Trodes time index
    systime : array_like, int64
        Unix time

    Returns
    -------
    adjusted_systime : array_like, int64
        Unix time

    """
    NANOSECONDS_TO_SECONDS = 1E9

    # Convert
    systime_seconds = np.asarray(systime).astype(
        np.float64) / NANOSECONDS_TO_SECONDS
    trodestime_index = np.asarray(trodestime).astype(np.float64)

    slope, intercept, r_value, p_value, std_err = linregress(
        trodestime_index, systime_seconds)
    adjusted_timestamps = intercept + slope * trodestime_index
    return (adjusted_timestamps * NANOSECONDS_TO_SECONDS).astype(np.int64)


def _insert_new_data(data_file, df):
    """
    Replaces the `data` in the extracted data file with a new one.

    Parameters
    ----------
    data_file : dict
        Original data file as read in by `readTrodesExtractedDataFile`
    df : pandas.DataFrame
        New data

    Returns
    -------
    new_data_file : dict
        Updated data file

    """
    new_data_file = data_file.copy()
    new_data_file['data'] = np.asarray(df.to_records(index=False))
    new_data_file['fields'] = ''.join(
        [f'<{name} {dtype}>'
         for name, (dtype, _) in new_data_file['data'].dtype.fields.items()])

    return new_data_file


def fix_timestamp_lag(continuoustime_filename):
    """
    Fix the correspondence between trodestime
    and system (wall) time.


    There is some jitter in the arrival times of packets from the MCU (as
    reflected in the sysclock records in the .rec file. If we assume that
    the Trodes clock is actually regular, and that any episodes of lag are
    fairly sporadic, we can recover the correspondence between trodestime
    and system (wall) time.

    Parameters
    ----------
    continuoustime_filename : str
        Path to .continuoustime.dat file

    """
    data_file = readTrodesExtractedDataFile(continuoustime_filename)

    if 'systime' not in data_file['data'].dtype.names:
        # logging.warn
        new_data = infer_systime(data_file)
    else:
        new_data = (
            pd.DataFrame(data_file['data'])
            .assign(
                time_chunk_label=lambda df: _label_time_chunks(df.trodestime))
            .assign(
                adjusted_systime=lambda df: _regress_timestamps(df.trodestime,
                                                                df.systime)))

    new_data_file = _insert_new_data(data_file, new_data)
    write_trodes_extracted_datafile(continuoustime_filename, new_data_file)
