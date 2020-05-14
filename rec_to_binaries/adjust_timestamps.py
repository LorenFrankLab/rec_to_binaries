import numpy as np
import pandas as pd
from scipy.stats import linregress

from rec_to_binaries.read_binaries import (readTrodesExtractedDataFile,
                                           write_trodes_extracted_datafile)


def _label_time_chunks(time_index):
    time_index = np.asarray(time_index)
    is_gap = np.diff(time_index) > 1
    is_gap = np.insert(is_gap, 0, False)
    return np.cumsum(is_gap)


def _regress_timestamps(trodestime, systime):
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

    new_data_file = data_file.copy()
    new_data_file['data'] = np.asarray(df.to_records(index=False))
    new_data_file['Fields'] = ''.join(
        [f'<{name} {dtype}>'
         for name, (dtype, _) in new_data_file['data'].dtype.fields.items()])

    return new_data_file


def fix_timestamp_lag(filename):
    data_file = readTrodesExtractedDataFile(filename)

    new_data = (
        pd.DataFrame(data_file['data'])
        .assign(time_chunk_label=lambda df: _label_time_chunks(df.trodestime))
        .assign(adjusted_systime=lambda df: _regress_timestamps(df.trodestime,
                                                                df.systime)))

    new_data_file = _insert_new_data(data_file, new_data)
    write_trodes_extracted_datafile(filename, new_data_file)
