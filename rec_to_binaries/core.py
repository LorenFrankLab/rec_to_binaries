import glob
import os
from logging import getLogger

import rec_to_binaries.trodes_data as td
from rec_to_binaries.adjust_timestamps import fix_timestamp_lag

_DEFAULT_LFP_EXPORT_ARGS = ('-highpass', '0', '-lowpass', '400',
                            '-interp', '0', '-userefs', '0',
                            '-outputrate', '1500')
_DEFAULT_MDA_EXPORT_ARGS = ('-usespikefilters', '0',
                            '-interp', '1', '-userefs', '0')
_DEFAULT_ANALOG_EXPORT_ARGS = ()
_DEFAULT_DIO_EXPORT_ARGS = ()
_DEFAULT_SPIKE_EXPORT_ARGS = ()
_DEFAULT_TIME_EXPORT_ARGS = ()

logger = getLogger(__name__)


def extract_trodes_rec_file(data_dir,
                            animal,
                            out_dir=None,
                            dates=None,
                            lfp_export_args=_DEFAULT_LFP_EXPORT_ARGS,
                            mda_export_args=_DEFAULT_MDA_EXPORT_ARGS,
                            analog_export_args=_DEFAULT_ANALOG_EXPORT_ARGS,
                            dio_export_args=_DEFAULT_DIO_EXPORT_ARGS,
                            spikes_export_args=_DEFAULT_SPIKE_EXPORT_ARGS,
                            time_export_args=_DEFAULT_TIME_EXPORT_ARGS,
                            make_HDF5=False,
                            extract_analog=True,
                            extract_spikes=True,
                            extract_lfps=True,
                            extract_dio=True,
                            extract_time=True,
                            extract_mda=True,
                            adjust_timestamps_for_mcu_lag=True,
                            make_mountain_dir=False,
                            make_pos_dir=True,
                            overwrite=False,
                            stop_error=False,
                            use_folder_date=False,
                            parallel_instances=1,
                            use_day_config=True):
    """Extracting Trodes rec files.

    Following the Frank Lab directory structure for raw ephys data, will
    automate extraction of Trode's rec files into its exploded datatype
    components, and then will convert the files to an hdf5 storage
    to be used for further preprocessing and analysis.

    To find any of the extract args (e.g. lfp_export_args) use the shell help
    i.e. `exportLFP -h` or refer to the trodes code repository documentation.

    Parameters
    ----------
    data_dir : str
    animal : str
        Name of animal
    out_dir : str, optional (default is None)
        Path to save preprocessed data (defaults to data_dir if None);
        subfolders [out_dir]/[animal]/[date]/preprocessing will be created.
    dates : list, optional (default is None)
        Only process select dates (defaults to all available dates if None)
    lfp_export_args : tuple, optional
        Parameters for SpikeGadgets `exportLFP` function
    mda_export_args : tuple, optional
        Parameters for SpikeGadgets `exportmda` function
    analog_export_args : tuple, optional
        Parameters for SpikeGadgets `exportanalog` function
    dio_export_args : tuple, optional
        Parameters for SpikeGadgets `exportdio` function
    spikes_export_args : tuple, optional
        Parameters for SpikeGadgets `exportspikes` function
    time_export_args : tuple, optional
        Parameters for SpikeGadgets `exporttime` function
    parallel_instances : int, optional
        Number of parallel jobs to run.
    make_HDF5 : bool, optional
        If true, will make HDF5 files in addition to binaries.
    extract_analog : bool, optional
        If true, extracts the analog data (accelerometer, gyroscope,
        magnetometor).
    extract_spikes : bool, optional
    extract_lfps : bool, optional
    extract_dio : bool, optional
    extract_time : bool, optional
    extract_mda : bool, optional
    adjust_timestamps_for_mcu_lag : bool, optional
        If True, fixes the correspondence between trodestime
        and system (wall) time due to MCU lag
    make_mountain_dir : bool, optional
    make_pos_dir : bool, optional
    overwrite : bool, optional
        If true, will overwrite existing files.
    stop_error : bool, optional
        If true, the function will stop on errors. If false it will only
        give warnings if something fails.
    use_folder_date : bool, optional
    use_day_config : bool, optional
        Use external configuration file in date folder
        (i.e. `<date>.trodesconf`)

    """
    animal_info = td.TrodesAnimalInfo(
        data_dir, animal, out_dir=out_dir, dates=dates)

    extractor = td.ExtractRawTrodesData(animal_info)
    raw_epochs_unionset = animal_info.get_raw_epochs_unionset()

    if len(raw_epochs_unionset) == 0:
        logger.warning('No epochs found!')
    raw_dates = animal_info.get_raw_dates()

    if extract_analog:
        logger.info('Extracting analog data...')
        extractor.extract_analog(
            raw_dates, raw_epochs_unionset, export_args=analog_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if extract_dio:
        logger.info('Extracting DIO...')
        extractor.extract_dio(
            raw_dates, raw_epochs_unionset, export_args=dio_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if extract_lfps:
        logger.info('Extracting LFP...')
        extractor.extract_lfp(
            raw_dates, raw_epochs_unionset, export_args=lfp_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if extract_mda:
        logger.info('Extracting mda...')
        extractor.extract_mda(
            raw_dates, raw_epochs_unionset, export_args=mda_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if extract_spikes:
        logger.info('Extracting spikes...')
        extractor.extract_spikes(
            raw_dates, raw_epochs_unionset, export_args=spikes_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if extract_time:
        logger.info('Extracting time...')
        extractor.extract_time(
            raw_dates, raw_epochs_unionset, export_args=time_export_args,
            overwrite=overwrite, stop_error=stop_error,
            use_folder_date=use_folder_date,
            parallel_instances=parallel_instances,
            use_day_config=use_day_config)

    if adjust_timestamps_for_mcu_lag:
        preprocessing_dir = animal_info.get_preprocessing_dir()
        filenames = glob.glob(os.path.join(
            preprocessing_dir, '**', '*.continuoustime.dat'), recursive=True)
        for file in filenames:
            fix_timestamp_lag(file)

    if make_mountain_dir:
        logger.info('Making mountain directory...')
        extractor.prepare_mountain_dir(
            raw_dates, raw_epochs_unionset, use_folder_date=use_folder_date,
            stop_error=stop_error)

    if make_pos_dir:
        logger.info('Making position directory...')
        extractor.prepare_pos_dir(
            raw_dates, raw_epochs_unionset, overwrite=overwrite,
            use_folder_date=use_folder_date, stop_error=stop_error)

    if make_HDF5:
        logger.info('Converting binaries into HDF5 files...')
        # Reload animal_info to get directory structures created during
        # extraction
        convert_binaries_to_hdf5(data_dir, animal, out_dir=out_dir,
                                 dates=dates,
                                 parallel_instances=parallel_instances)


def convert_binaries_to_hdf5(data_dir, animal, out_dir=None, dates=None,
                             parallel_instances=1,
                             convert_dio=True,
                             convert_lfp=True,
                             convert_pos=True,
                             convert_spike=True):
    animal_info = td.TrodesAnimalInfo(
        data_dir, animal, out_dir=out_dir, dates=dates)
    """Converting preprocessed binaries into HDF5 files.

    Assume that preprocessing has already been completed using (for example)
    extract_trodes_rec_file.

    Parameters
    ----------
    data_dir : str
    animal : str
        Name of animal
    out_dir : str, optional (default is None)
        Path to save preprocessed data (defaults to data_dir if None);
        subfolders [out_dir]/[animal]/[date]/preprocessing will be created.
    dates : list, optional (default is None)
        Only process select dates (defaults to all available dates if None)
    parallel_instances : int, optional
        Number of parallel jobs to run.
    convert_spikes : bool, optional
    convert_lfps : bool, optional
    convert_dio : bool, optional
    convert_mda : bool, optional
    """

    importer = td.TrodesPreprocessingToAnalysis(animal_info)

    # Convert binaries into hdf5 files
    if convert_dio:
        for date in animal_info.preproc_dio_paths['date'].unique():
            logger.info(f'converting dio for {date} ...')
            importer.convert_dio_day(date)

    if convert_lfp:
        for date in animal_info.preproc_LFP_paths['date'].unique():
            logger.info(f'converting LFP for {date} ...')
            importer.convert_lfp_day(date)

    if convert_pos:
        for date in animal_info.preproc_pos_paths['date'].unique():
            logger.info(f'converting pos for {date} ...')
            importer.convert_pos_day(date)

    if convert_spike:
        for date in animal_info.preproc_spike_paths['date'].unique():
            logger.info(f'converting spike for {date} ...')
            importer.convert_spike_day(
                date, parallel_instances=parallel_instances)
