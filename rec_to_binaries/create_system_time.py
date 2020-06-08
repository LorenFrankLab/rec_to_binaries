import numpy as np
import pandas as pd


def infer_systime(data_file):
    systime = create_systime(data_file['clockrate'],
                             data_file['data'],
                             data_file['system_time_at_creation'])
    n_time = systime.shape[0]
    trodestime = data_file['data']['trodestime'].copy()
    time_chunk_label = np.ones(n_time, dtype=np.int)
    adjusted_systime = systime.copy()

    return pd.DataFrame(
        {'trodestime': trodestime,
         'systime': systime,
         'time_chunk_label': time_chunk_label,
         'adjusted_systime': adjusted_systime,
         })


def create_systime(clockrate, data, system_time_at_creation):
    """Creates the system time by extrapolating from the
    'system_time_at_creation' timestamp as a function of the 'clockrate' and
    the 'trodestime' containted in 'data'

    Parameters
    ----------
    clockrate : int
    data : np.ndarray
    system_time_at_creation : int


    Returns
    -------
    systime

    Notes
    -----
    Assumes 'clockrate' is in Hz and 'system_time_at_creation' is taken to the
    millisecond

    """
    NANOSECONDS_TO_SECONDS = 1e9

    clockrate = int(clockrate)
    n_time = data.shape[0]
    system_time_at_creation = pd.to_datetime(
        int(system_time_at_creation), unit='ms').value
    end = (system_time_at_creation +
           int((n_time - 1) * NANOSECONDS_TO_SECONDS / clockrate))

    systime = pd.date_range(
        start=system_time_at_creation,
        end=end,
        periods=n_time,
    ).astype(np.int64).to_numpy()

    return systime
