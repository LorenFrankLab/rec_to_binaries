import numpy as np
import pandas as pd
from rec_to_binaries.read_binaries import (readTrodesExtractedDataFile,
                                           write_trodes_extracted_datafile)


def add_system_time_to_file(continuous_time_file, new_file_name):
    """Adds system time to the continuoustime.dat file created by Trodes
    exporttime command.

    Parameters
    ----------
    continuous_time_file : str
        Filepath to the binary file <date_animal_run>.continuoustime.dat
    new_file_name: str
        Filepath to the binary output file <date_animal_run>.continuoustime.dat
        which contains the added continuoustime.dat to the 'data' field. Must
        include the 'contintinuoustime.dat' in the string. Writes out the
        complete .continuoustime.dat file specified by new_file_name.

    """
    cont_time = readTrodesExtractedDataFile(continuous_time_file)
    cont_time = {key.lower(): value for key, value in cont_time.items()}
    cont_time['data'] = create_and_add_system_timepoints(cont_time)
    cont_time['fields'] = '<trodestime uint32><systime int64>'

    write_trodes_extracted_datafile(new_file_name, cont_time)


def create_and_add_system_timepoints(cont_time):
    """Creates the system time by extrapolating from the
    'system_time_at_creation' timestamp as a function of the 'clockrate' and
    the 'trodestime' containted in 'data'

    Parameters
    ----------
    cont_time: dict
        A dictionary created by `readTrodesExtractedDataFile`

    Notes
    -----
    Assumes 'clockrate' is in Hz and 'system_time_at_creation' is taken to the
    millisecond

    """
    NANOSECONDS_TO_SECONDS = 1e9

    clockrate = int(cont_time['clockrate'])
    n_time = cont_time['data'].shape[0]
    start = int(cont_time['system_time_at_creation'])
    end = start + int((n_time - 1) * NANOSECONDS_TO_SECONDS / clockrate)

    systime = pd.date_range(
        start=start,
        end=end,
        periods=n_time,
    ).astype(np.int64).to_numpy()

    return package_sys_time_with_trodes_time(systime, cont_time)


def package_sys_time_with_trodes_time(sys_time, cont_time):
    """Packages the system_time created by create_and_add_system_timepoints

    Parameters
    ----------
    cont_time: dict
        A dictionary created by `readTrodesExtractedDataFile`
    sys_time: numpy.ndarray
        An array of extrapolated system time points, to the nanosecond

    Returns
    ----------
    packaged_data: numpy.array
        A structured array where the columns are `trodestime` and `systime`.

    Notes
    -----
    data_type reflects the type casted in binaries produced by Trodes 1.8


    """
    data_type = np.dtype([('trodestime', np.uint32), ('systime', np.int64)])

    packaged_data = np.zeros((len(sys_time),), dtype=data_type)

    packaged_data['trodestime'] = cont_time['data']

    packaged_data['systime'] = sys_time

    return packaged_data
