import functools
import itertools
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import time
import warnings

import numpy as np
import pandas as pd
from rec_to_binaries.binary_utils import (TrodesDIOBinaryLoader,
                                          TrodesLFPBinaryLoader,
                                          TrodesPosBinaryLoader,
                                          TrodesSpikeBinaryLoader,
                                          TrodesTimestampBinaryLoader)


class TrodesDataFormatWarning(RuntimeWarning):
    pass


class TrodesDataFormatError(RuntimeError):
    pass


class TrodesAnimalInfoError(RuntimeError):
    pass


class TrodesRawFileNameParser:

    trodes_filename_re = re.compile(
        '^(\d*)_([a-zA-Z0-9]*)_(\d*)_{0,1}(\w*)\.{0,1}(.*)\.([a-zA-Z0-9]*)$')

    def __init__(self, filename_str):
        self.filename = filename_str
        filename_match = self.trodes_filename_re.match(self.filename)

        if filename_match is not None:
            filename_groups = filename_match.groups()
            try:
                self.date = filename_groups[0]
                self.date_expand = TrodesRawFileNameParser.expand_date_str(
                    self.date)

            except ValueError:
                raise TrodesDataFormatError('Filename ({}) date field is not a true date.'.
                                            format(filename_str))

            self.name_str = filename_groups[1]
            self.epochlist_str = filename_groups[2]
            epochlist = re.findall('\d\d', self.epochlist_str)
            if len(epochlist) == 0:
                raise TrodesDataFormatError(('Filename ({}) does not match basic trodes file format, epoch list '
                                             'could not be parsed.').format(filename_str))
            self.epochtuple = tuple([int(epoch_str)
                                     for epoch_str in epochlist])
            self.label = filename_groups[3]
            self.label_ext = filename_groups[4]
            self.ext = filename_groups[5]

            self.filename_no_ext = re.match(
                '^(.*)\.(.*)$', self.filename).groups()[0]
        else:
            raise TrodesDataFormatError('Filename ({}) does not match basic trodes file format.'.
                                        format(filename_str))

    @staticmethod
    def expand_date_str(date_str):
        return time.strptime(date_str, '%Y%m%d')


class TrodesSpikeExtractedFileNameParser(TrodesRawFileNameParser):
    def __init__(self, filename_str):
        super().__init__(filename_str)

        if self.label_ext == 'exportspikes' and self.ext == 'log':
            self.export_logfile = True
            self.ntrode = None
            self.time_label = None
        else:
            self.export_logfile = False
            label_match = re.match('^.*_nt(\d*)\.{0,1}(.*)$', self.label_ext)

            if label_match is not None and self.ext == 'dat':
                label_match_group = label_match.groups()
                self.ntrode = int(label_match_group[0])
                self.time_label = label_match_group[1]
            else:
                raise TrodesDataFormatError('Filename ({}) does not match ({}) format.'.
                                            format(filename_str, self.__class__.__name__))


class TrodesLFPExtractedFileNameParser(TrodesRawFileNameParser):
    def __init__(self, filename_str):
        super().__init__(filename_str)

        if self.label_ext == 'exportLFP' and self.ext == 'log':
            self.export_logfile = True
            self.timestamp_file = None
            self.time_label = None
            self.channel = None
            self.ntrode = None

        else:
            self.export_logfile = False
            timestamp_label_match = re.match(
                '^timestamps\.{0,1}(.*)$', self.label_ext)
            if timestamp_label_match is not None and self.ext == 'dat':
                self.timestamp_file = True
                self.time_label = timestamp_label_match.groups()[0]
                self.channel = None
                self.ntrode = None
            else:
                self.timestamp_file = False
                self.time_label = None
                label_match = re.match('^.*_nt(\d*)ch(\d*)$', self.label_ext)

                if label_match is not None and self.ext == 'dat':
                    label_match_groups = label_match.groups()
                    self.ntrode = int(label_match_groups[0])
                    self.channel = int(label_match_groups[1])
                else:
                    raise TrodesDataFormatError('Filename ({}) does not match ({}) format.'.
                                                format(filename_str, self.__class__.__name__))


class TrodesMdaExtractedFileNameParser(TrodesRawFileNameParser):
    def __init__(self, filename_str):
        super().__init__(filename_str)

        if self.label_ext == 'exportmda' and self.ext == 'log':
            self.export_logfile = True
            self.timestamp_file = None
            self.time_label = None
            self.ntrode = None
        else:
            self.export_logfile = False
            timestamp_label_match = re.match(
                '^timestamps\.{0,1}(.*)$', self.label_ext)
            if timestamp_label_match is not None and self.ext == 'mda':
                self.timestamp_file = True
                self.time_label = timestamp_label_match.groups()[0]
                self.ntrode = None
            else:
                self.timestamp_file = False
                self.time_label = None
                label_match = re.match('^nt(\d*)$', self.label_ext)

                if label_match is not None and self.ext == 'mda':
                    label_match_groups = label_match.groups()
                    self.ntrode = int(label_match_groups[0])
                else:
                    raise TrodesDataFormatError('Filename ({}) does not match ({}) format.'.
                                                format(filename_str, self.__class__.__name__))


class TrodesDIOExtractedFileNameParser(TrodesRawFileNameParser):
    def __init__(self, filename_str):
        super().__init__(filename_str)

        if self.label_ext == 'exportdio' and self.ext == 'log':
            self.export_logfile = True
            self.time_label = None
            self.channel = None
            self.direction = None
        else:
            self.export_logfile = False

            label_match = re.match(
                '^dio_([A-Za-z]*)(\d*)\.{0,1}(.*)$', self.label_ext)

            if label_match is not None and self.ext == 'dat':
                label_match_groups = label_match.groups()
                # string in/out
                self.direction = label_match_groups[0][1:].lower()
                # Din/Dout channel
                self.channel = int(label_match_groups[1])
                self.time_label = label_match_groups[2]

            else:
                raise TrodesDataFormatError('Filename ({}) does not match ({}) format.'.
                                            format(filename_str, self.__class__.__name__))


class TrodesPosExtractedFileNameParser(TrodesRawFileNameParser):
    def __init__(self, filename_str):
        super().__init__(filename_str)
        label_ext_match = re.match('^(\d*)\.?(.*)$', self.label_ext)
        self.label_ext1 = label_ext_match.groups()[0]
        self.label_ext2 = label_ext_match.groups()[1]

        timestamp_label_match = re.match(
            '^pos_timestamps\.{0,1}(.*)$', self.label_ext2)
        if timestamp_label_match is not None and self.ext == 'dat':
            self.timestamp_file = True
            self.time_label = timestamp_label_match.groups()[0]
            self.pos_label = None
        else:
            self.timestamp_file = False
            self.time_label = None
            label_match = re.match('^pos_(.*)$', self.label_ext2)
            if label_match is not None and self.ext == 'dat':
                self.pos_label = label_match.groups()[0]
            else:

                raise TrodesDataFormatError('Filename ({}) does not match ({}) format.'.
                                            format(filename_str, self.__class__.__name__))


class TrodesAnimalInfo:

    def __init__(self, base_dir, anim_name, RawFileParser=TrodesRawFileNameParser,
                 out_dir=None, dates=None):
        self.RawFileNameParser = RawFileParser
        self.base_dir = base_dir
        self.anim_name = anim_name

        # optionally choose a different output path to save preprocessed data
        if out_dir is not None:
            self.out_dir = out_dir
        else:
            self.out_dir = base_dir  # default (legacy behavior)

        raw_path = self._get_raw_dir(base_dir, anim_name)

        raw_day_paths = self._get_day_dirs(raw_path)

        self.raw_rec_files = {}
        self.raw_pos_files = {}
        self.raw_h264_files = {}
        self.raw_postime_files = {}
        self.raw_date_trodesconf = {}
        self.raw_poshwframecount_files = {}
        self.raw_trodescomments_files = {}

        # Loads and caches all raw data files that exist
        for date, day_path in raw_day_paths.items():
            if dates is not None:
                # if dates given, only work on these selected dates
                if date not in dates:
                    continue
            self.raw_rec_files[date] = {}
            day_rec_filenames = self._get_rec_paths(
                day_path, self.RawFileNameParser)
            for rec_filename_parsed, rec_path in day_rec_filenames:
                if rec_filename_parsed.date != date:
                    warnings.warn(('For rec file ({}) the date field does not match '
                                   'the folder date ({}). This should be fixed or could have'
                                   'unintended parsing consequences.').
                                  format(rec_filename_parsed.filename, date), TrodesDataFormatWarning)
                self.raw_rec_files[date][rec_filename_parsed.epochtuple] = (
                    rec_filename_parsed, rec_path)

            self.raw_pos_files[date] = {}
            day_pos_filenames = self._get_video_tracking_paths(
                day_path, self.RawFileNameParser)
            for pos_filename_parsed, pos_path in day_pos_filenames:
                raw_pos_file_date_epoch = self.raw_pos_files[date].setdefault(
                    pos_filename_parsed.epochtuple, {})
                raw_pos_file_date_epoch[pos_filename_parsed.label_ext] = (
                    pos_filename_parsed, pos_path)

            self.raw_h264_files[date] = {}
            day_h264_filenames = self._get_h264_paths(
                day_path, self.RawFileNameParser)
            for h264_filename_parsed, h264_path in day_h264_filenames:
                raw_h264_file_date_epoch = self.raw_h264_files[date].setdefault(
                    h264_filename_parsed.epochtuple, {})
                raw_h264_file_date_epoch[h264_filename_parsed.label_ext] = (
                    h264_filename_parsed, h264_path)

            self.raw_postime_files[date] = {}
            day_postime_filenames = self._get_video_timestamp_paths(
                day_path, self.RawFileNameParser)
            for postime_filename_parsed, postime_path in day_postime_filenames:
                raw_postime_file_date_epoch = self.raw_postime_files[date]. \
                    setdefault(postime_filename_parsed.epochtuple, {})
                raw_postime_file_date_epoch[postime_filename_parsed.label_ext] = \
                    (postime_filename_parsed, postime_path)

            self.raw_poshwframecount_files[date] = {}
            day_poshwframecount_filenames = self._get_video_hwframecount_paths(
                day_path, self.RawFileNameParser)
            for poshwframecount_filename_parsed, poshwframecount_path in day_poshwframecount_filenames:
                raw_poshwframecount_file_date_epoch = self.raw_poshwframecount_files[date]. \
                    setdefault(poshwframecount_filename_parsed.epochtuple, {})
                raw_poshwframecount_file_date_epoch[poshwframecount_filename_parsed.label_ext] = \
                    (poshwframecount_filename_parsed, poshwframecount_path)

            self.raw_trodescomments_files[date] = {}
            day_trodescomments_filenames = self._get_trodes_comments_paths(
                day_path, self.RawFileNameParser)
            for trodescomments_filename_parsed, trodescomments_path in day_trodescomments_filenames:
                self.raw_trodescomments_files[date][trodescomments_filename_parsed.epochtuple] = \
                    (trodescomments_filename_parsed, trodescomments_path)

            day_trodesconf_paths = self._get_trodesconf_paths(day_path)
            for trodesconf_path in day_trodesconf_paths:
                if re.match('^(.*).trodesconf$', os.path.basename(trodesconf_path)).groups()[0] == date:
                    self.raw_date_trodesconf[date] = trodesconf_path

        # Load and store all preprocessing
        preprocessing_date_path_dict = self._get_preprocessing_date_path_dict(
            self.get_preprocessing_dir())
        self.preproc_datatype_dirs = self._get_preprocessing_date_data_path_df(
            preprocessing_date_path_dict)

        lfp_directory_entries = self.preproc_datatype_dirs[
            self.preproc_datatype_dirs['datatype'] == 'LFP']

        self.preproc_LFP_paths = (
            TrodesAnimalInfo._get_extracted_datatype_paths_df(
                lfp_directory_entries,
                ['ntrode', 'channel', 'timestamp_file', 'time_label',
                 'export_logfile'],
                ['date', 'epoch', 'label_ext', 'ntrode', 'channel'],
                TrodesLFPExtractedFileNameParser))

        spike_directory_entries = self.preproc_datatype_dirs[
            self.preproc_datatype_dirs['datatype'] == 'spikes']

        self.preproc_spike_paths = (
            TrodesAnimalInfo._get_extracted_datatype_paths_df(
                spike_directory_entries,
                ['time_label', 'ntrode', 'export_logfile'],
                ['date', 'epoch', 'label_ext', 'time_label', 'ntrode'],
                TrodesSpikeExtractedFileNameParser))

        dio_directory_entries = self.preproc_datatype_dirs[
            self.preproc_datatype_dirs['datatype'] == 'DIO']

        self.preproc_dio_paths = (
            TrodesAnimalInfo._get_extracted_datatype_paths_df(
                dio_directory_entries,
                ['time_label', 'direction', 'channel', 'export_logfile'],
                ['date', 'epoch', 'label_ext', 'time_label', 'direction',
                 'channel'],
                TrodesDIOExtractedFileNameParser))

        mda_directory_entries = self.preproc_datatype_dirs[
            self.preproc_datatype_dirs['datatype'] == 'mda']

        self.preproc_mda_paths = (
            TrodesAnimalInfo._get_extracted_datatype_paths_df(
                mda_directory_entries,
                ['timestamp_file', 'time_label', 'ntrode', 'export_logfile'],
                ['date', 'epoch', 'label_ext', 'ntrode'],
                TrodesMdaExtractedFileNameParser))

        pos_directory_entries = self.preproc_datatype_dirs[
            self.preproc_datatype_dirs['datatype'] == 'pos']

        self.preproc_pos_paths = (
            TrodesAnimalInfo._get_extracted_datatype_paths_df(
                pos_directory_entries,
                ['timestamp_file', 'time_label', 'pos_label'],
                ['date', 'epoch', 'label_ext', 'pos_label'],
                TrodesPosExtractedFileNameParser))

    def __repr__(self):
        return ("TrodesAnimalInfo("
                f"anim_name={self.__dict__['anim_name']}, "
                f"base_dir={self.__dict__['base_dir']})")

    @staticmethod
    def _get_extracted_datatype_paths_df(directory_entries_df, parser_datatype_fields, sort_on_fields,
                                         ExtractedFileParser):
        """

        Args:
            directory_entries_df: Panda table that contains directory list for single datatype
                must have at least a 'directory' column and a unique index
            parser_datatype_fields: fields found in ExtractedFileParser ot read and add to the return table
                (must be ordered list)
            sort_on_fields: fields to sort final table on (pd.DataFrame.sort_values)
            ExtractedFileParser: The file parser for single data type

        Returns:
            Panda table with the paths of all files in each directory, merged with the original directory_entries_df
            with the directory column dropped

        """
        partial_extracted_columns = parser_datatype_fields + \
            ['dir_index', 'path']
        partial_extracted_paths = pd.DataFrame(
            columns=partial_extracted_columns)
        for dir_index, directory in directory_entries_df['directory'].iteritems():
            file_list = TrodesAnimalInfo._get_extracted_file_list(
                directory, ExtractedFileParser=ExtractedFileParser)
            directory_path_fields = []
            for filename_parser, file_path in file_list:
                file_path_fields = []
                for field in parser_datatype_fields:
                    file_path_fields.append(
                        filename_parser.__getattribute__(field))

                file_path_fields.append(dir_index)
                file_path_fields.append(file_path)

                directory_path_fields.append(file_path_fields)
            partial_extracted_paths = (partial_extracted_paths
                                       .append(pd.DataFrame(directory_path_fields,
                                                            columns=partial_extracted_columns),
                                               ignore_index=True))
        datatype_paths_df = (directory_entries_df.drop('directory', 1).merge(right=partial_extracted_paths,
                                                                             left_index=True,
                                                                             right_on='dir_index')
                             .sort_values(sort_on_fields)
                             .reset_index(drop=True))

        return datatype_paths_df

    def get_raw_dates(self):
        return sorted(self.raw_rec_files.keys())

    def get_raw_epochs_unionset(self):
        unionset = set()
        for day in self.get_raw_dates():
            allepochtuples = self.raw_rec_files[day].keys()
            for epochtuple in allepochtuples:
                for epoch in epochtuple:
                    unionset.add(epoch)

        return unionset

    @staticmethod
    def _lookup_date_epoch_dict(nested_dict, date, epoch):
        date_dict = nested_dict[date]
        return_val = None
        for epochtuple, epoch_val in date_dict.items():
            if epoch in epochtuple:
                if return_val is None:
                    return_val = epoch_val
                else:
                    raise TrodesAnimalInfoError(('date ({}) and epoch ({}) index '
                                                 'returns more than one possible value. '
                                                 'Likely the file structure for '
                                                 'is invalid and should be fixed.')
                                                .format(date, epoch))

        return return_val

    def get_raw_trodescomments_path(self, date, epoch):
        trodescomments_path = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_trodescomments_files, date, epoch)
        if trodescomments_path is None:
            raise KeyError(('Trodes comment file does not exist '
                            'for animal ({}), date ({}) and epoch ({}).').
                           format(self.anim_name, date, epoch))
        return trodescomments_path

    def get_raw_h264_paths(self, date, epoch):
        h264_paths = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_h264_files, date, epoch)
        if h264_paths is None:
            raise KeyError(('Raw h264 video file does not exist '
                            'for animal ({}), date ({}) and epoch ({}).').
                           format(self.anim_name, date, epoch))
        return h264_paths

    def get_raw_h264_path(self, date, epoch, label_ext):
        return self.get_raw_h264_paths(date, epoch)[label_ext]

    def get_raw_pos_paths(self, date, epoch):
        pos_paths = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_pos_files, date, epoch)
        if pos_paths is None:
            raise KeyError(('Raw/online position tracking file does not exist '
                            'for animal ({}), date ({}) and epoch ({}).').
                           format(self.anim_name, date, epoch))

        return pos_paths

    def get_raw_pos_path(self, date, epoch, label_ext):
        return self.get_raw_pos_paths(date, epoch)[label_ext]

    def get_raw_postime_paths(self, date, epoch):
        postime_paths = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_postime_files, date, epoch)
        if postime_paths is None:
            raise KeyError('Online position timestamps file does not exist for animal ({}), date ({}) and epoch ({}).'.
                           format(self.anim_name, date, epoch))

        return postime_paths

    def get_raw_postime_path(self, date, epoch, label_ext):
        return self.get_raw_postime_paths(date, epoch)[label_ext]

    def get_raw_poshwframecount_paths(self, date, epoch):
        poshwframecount_paths = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_poshwframecount_files, date, epoch)
        if poshwframecount_paths is None:
            raise KeyError(('Online position hwFrameCount file does not exist for '
                            'animal ({}), date ({}) and epoch ({}).').
                           format(self.anim_name, date, epoch))
        return poshwframecount_paths

    def get_raw_poshwframecount_path(self, date, epoch, label_ext):
        return self.get_raw_poshwframecount_paths(date, epoch)[label_ext]

    def get_raw_rec_path(self, date, epoch):
        rec_path = TrodesAnimalInfo._lookup_date_epoch_dict(
            self.raw_rec_files, date, epoch)
        if rec_path is None:
            raise KeyError(('Rec files does not exist for '
                            'animal ({}), date ({}) and epoch ({}).').
                           format(self.anim_name, date, epoch))
        return rec_path

    def get_raw_dir(self):
        return self._get_raw_dir(self.base_dir, self.anim_name)

    def get_preprocessing_dir(self):
        return self._get_preprocessing_dir(self.out_dir, self.anim_name)

    def get_analysis_dir(self):
        return self._get_analysis_dir(self.out_dir, self.anim_name)

    def get_preprocessing_date_dir(self, date, stop_error=True):
        path = os.path.join(self.get_preprocessing_dir(), date)
        if not os.path.isdir(path) and stop_error:
            if os.path.exists(path):
                raise TrodesAnimalInfoError('Animal {}, path ({}) exists but is not a directory.'.format(self.anim_name,
                                                                                                         path))
            else:
                raise TrodesAnimalInfoError('Animal {}, path ({}) does not exist.'.format(self.anim_name,
                                                                                          path))

        return path

    def get_date_trodesconf(self, date):
        return self.raw_date_trodesconf[date]

    def _get_preprocessing_date_path_dict(self, preprocess_path):
        return self._get_day_dirs(preprocess_path)

    @staticmethod
    def _get_preprocessing_date_data_path_df(date_path_dict):
        full_data_paths = pd.DataFrame(
            columns=['date', 'epoch', 'label_ext', 'datatype', 'directory'])
        for date, date_path in date_path_dict.items():
            date_path_entries = os.scandir(date_path)
            for date_path_entry in date_path_entries:
                if date_path_entry.is_dir():
                    try:
                        entry_name_parser = TrodesRawFileNameParser(
                            date_path_entry.name)
                        full_data_paths = full_data_paths.append(dict(zip(full_data_paths.columns,
                                                                          [date,
                                                                           entry_name_parser.epochtuple,
                                                                           entry_name_parser.label_ext,
                                                                           entry_name_parser.ext,
                                                                           date_path_entry.path])),
                                                                 ignore_index=True)
                    except TrodesDataFormatError as err:
                        warnings.warn(('Invalid folder name in preprocessing folder date ({}) folder ({}), ignoring.'.
                                       format(date, date_path_entry.name)))
        # sort and reindex paths
        full_data_paths = full_data_paths.sort_values(
            ['date', 'epoch', 'label_ext', 'datatype']).reset_index(drop=True)

        return full_data_paths

    @staticmethod
    def _get_extracted_file_list(path, ExtractedFileParser=TrodesRawFileNameParser):
        dir_entries = os.scandir(path)
        file_list = []
        for dir_entry in dir_entries:
            if dir_entry.is_file:
                try:
                    filename_parser = ExtractedFileParser(dir_entry.name)
                    file_list.append((filename_parser, dir_entry.path))
                except TrodesDataFormatError:
                    warnings.warn('File ({}) does not match file parser ({}). Skipping.'.
                                  format(dir_entry.path,
                                         ExtractedFileParser.__name__),
                                  TrodesDataFormatWarning)
        return file_list

    @staticmethod
    def _expand_str_date(date_str):
        return time.strptime(date_str, '%Y%m%d')

    @staticmethod
    def _get_raw_dir(base_dir, anim_name):
        return os.path.join(base_dir, anim_name, 'raw')

    @staticmethod
    def _get_analysis_dir(base_dir, anim_name):
        return os.path.join(base_dir, anim_name, 'analysis')

    @staticmethod
    def _get_preprocessing_dir(base_dir, anim_name):
        return os.path.join(base_dir, anim_name, 'preprocessing')

    @staticmethod
    def _get_day_dirs(anim_path):
        anim_day_paths = {}
        try:
            anim_dir_entries = os.scandir(anim_path)
            for anim_dir_entry in anim_dir_entries:
                if anim_dir_entry.is_dir():
                    try:
                        TrodesAnimalInfo._expand_str_date(anim_dir_entry.name)
                        anim_day_paths[anim_dir_entry.name] = anim_dir_entry.path
                    except ValueError:
                        warnings.warn(('animal path ({}) contains a data directory ({}) '
                                       'that does not conform to date format %Y%m%d.').
                                      format(anim_path, anim_dir_entry.name), TrodesDataFormatWarning)
        except FileNotFoundError:
            warnings.warn(('anim path ({}) does not exist.'.format(
                anim_path)), TrodesDataFormatWarning)
        return anim_day_paths

    @staticmethod
    def _get_rec_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        dir_entries = os.scandir(path)
        anim_rec_paths = []

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                # look only at rec files, ignore others
                if re.match('^.*\.rec$', dir_entry.name):
                    # check to see if filename format is good
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        anim_rec_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes rec filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return anim_rec_paths

    @staticmethod
    def _get_video_tracking_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        anim_pos_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*\.videoPositionTracking$', dir_entry.name):
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        anim_pos_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes videoPositionTracking filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return anim_pos_paths

    @staticmethod
    def _get_h264_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        anim_h264_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*\.h264$', dir_entry.name):
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        anim_h264_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes h264 filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return anim_h264_paths

    @staticmethod
    def _get_video_timestamp_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        anim_video_times_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*\.videoTimeStamps$', dir_entry.name):
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        anim_video_times_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes videoTimeStamps filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return anim_video_times_paths

    @staticmethod
    def _get_video_hwframecount_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        anim_video_hwframecount_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*\.videoTimeStamps\.(?:cameraHWFrameCount$|cameraHWSync)', dir_entry.name):
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        anim_video_hwframecount_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes videoTimeStamps.cameraHWFrameCount filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return anim_video_hwframecount_paths

    @staticmethod
    def _get_trodes_comments_paths(path, RawFileNameParser=TrodesRawFileNameParser):
        trodes_comment_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*\.trodesComments$', dir_entry.name):
                    try:
                        trodes_filename_parsed = RawFileNameParser(
                            dir_entry.name)
                        trodes_comment_paths.append(
                            (trodes_filename_parsed, dir_entry.path))
                    except TrodesDataFormatError:
                        warnings.warn(('Invalid trodes .trodesComments filename ({}), '
                                       'cannot be parsed, skipping.').
                                      format(dir_entry.path), TrodesDataFormatWarning)

        return trodes_comment_paths

    @staticmethod
    def _get_trodesconf_paths(path):
        trodesconf_paths = []

        dir_entries = os.scandir(path)

        for dir_entry in dir_entries:
            if dir_entry.is_file():
                if re.match('^.*.trodesconf$', dir_entry.name):
                    trodesconf_paths.append(dir_entry.path)

        return trodesconf_paths


class TrodesPreprocessingLFPEpoch:
    def __init__(self, anim: TrodesAnimalInfo, date, epochtuple):

        self.anim = anim
        self.date = date
        self.epochtuple = epochtuple

        LFP_paths = anim.preproc_LFP_paths[(anim.preproc_LFP_paths['date'] == date) &
                                           (anim.preproc_LFP_paths['epoch'] == epochtuple)]
        self.LFP_data_paths = LFP_paths[LFP_paths['timestamp_file'] == False]
        self.LFP_timestamp_paths = LFP_paths[LFP_paths['timestamp_file'] == True]

        self.lfp = pd.DataFrame()
        for path_tup in self.LFP_data_paths.itertuples():
            if not np.isnan(path_tup.ntrode) and not np.isnan(path_tup.channel):
                lfp_bin = TrodesLFPBinaryLoader(path_tup.path)
                single_col = pd.MultiIndex.from_tuples([(path_tup.ntrode, path_tup.channel)],
                                                       names=['ntrode', 'channel'])
                self.lfp = pd.concat([self.lfp, pd.DataFrame(lfp_bin.data, columns=single_col)], axis=1,
                                     verify_integrity=True)
            else:
                warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                               'has a bad preprocessing path entry, ntrode or '
                               'channel has a nan entry that is not a timestamp '
                               'file, skipping.').format(anim.anim_name, date, epochtuple))

        # get default timestamp
        try:
            orig_timestamp_path_entries = self.LFP_timestamp_paths[
                self.LFP_timestamp_paths['time_label'] == '']
            orig_timestamp_path = orig_timestamp_path_entries['path'].values[0]
            if len(orig_timestamp_path_entries) > 1:
                warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                               'has multiple original timestamp path entries, '
                               'using ({}).').format(anim.anim_name, date, epochtuple, orig_timestamp_path))
            orig_timestamp_bin = TrodesTimestampBinaryLoader(
                orig_timestamp_path)
            self.orig_timestamps = orig_timestamp_bin.data
        except (IndexError, FileNotFoundError):
            self.orig_timestamps = None
            raise TrodesDataFormatError(('Animal ({}), date ({}), epoch ({}) '
                                         'missing default timestamps file.').format(anim.anim_name, date, epochtuple))

        try:
            adj_timestamp_path_entries = self.LFP_timestamp_paths[
                self.LFP_timestamp_paths['time_label'] == 'adj']
            adj_timestamp_path = adj_timestamp_path_entries['path'].values[0]
            if len(adj_timestamp_path_entries) > 1:
                warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                               'has multiple adjusted timestamp path entries, '
                               'using ({}).').format(anim.anim_name, date, epochtuple, adj_timestamp_path))
            adj_timestamp_bin = TrodesTimestampBinaryLoader(adj_timestamp_path)
            self.adj_timestamps = adj_timestamp_bin.data
        except (IndexError, FileNotFoundError):
            self.adj_timestamps = None
            warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                           'missing adjusted timestamps file.').format(anim.anim_name, date, epochtuple),
                          TrodesDataFormatWarning)

        # always use original timestamp
        self.lfp.set_index(keys=self.orig_timestamps, inplace=True)


class TrodesPreprocessingSpikeEpoch:

    def __init__(self, anim: TrodesAnimalInfo, date, epochtuple, time_label, parallel_instances=1):
        self.spike_paths = anim.preproc_spike_paths[(anim.preproc_spike_paths['date'] == date) &
                                                    (anim.preproc_spike_paths['epoch'] == epochtuple) &
                                                    (anim.preproc_spike_paths['time_label'] == time_label)]
        self.anim = anim
        self.date = date
        self.epochtuple = epochtuple
        # index (ntrode_index)
        self.spikes = {}

        path_list = []
        ntrode_list = []
        for path_tup in self.spike_paths.itertuples():
            if not pd.isnull(path_tup.ntrode):
                path_list.append(path_tup.path)
                ntrode_list.append(path_tup.ntrode)
            else:
                warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                               'has a bad preprocessing path entry, ntrode '
                               'has a nan entry that is not a timestamp '
                               'file, skipping.').format(anim.anim_name, date, epochtuple))

        p = multiprocessing.Pool(parallel_instances)
        spikes_loaded = p.map(TrodesSpikeBinaryLoader, path_list, chunksize=1)
        self.spikes = dict(
            zip(ntrode_list, [loader.spikes for loader in spikes_loaded]))
        p.close()


class TrodesPreprocessingPosEpoch:
    def __init__(self, anim: TrodesAnimalInfo, date, epochtuple):
        self.anim = anim
        self.date = date
        self.epochtuple = epochtuple

        self.pos_paths = anim.preproc_pos_paths[(anim.preproc_pos_paths['date'] == date) &
                                                (anim.preproc_pos_paths['epoch'] == epochtuple)]

        self.timestamps = {}
        self.pos = {}
        for path_tup in self.pos_paths.itertuples():
            if path_tup.timestamp_file:
                if path_tup.time_label in self.timestamps:
                    warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                                   'has multiple timestamps with same label, using first one.').
                                  format(anim.anim_name, date, epochtuple))
                    break
                timestamp_bin = TrodesTimestampBinaryLoader(path_tup.path)
                self.timestamps[path_tup.time_label] = timestamp_bin.data
            elif not pd.isnull(path_tup.pos_label):
                # assume path is for a position file
                if path_tup.pos_label in self.pos:
                    warnings.warn(('Animal ({}), date ({}), epoch ({}) '
                                   'has multiple pos data with same label, using first one.').
                                  format(anim.anim_name, date, epochtuple))
                    break
                pos_bin = TrodesPosBinaryLoader(path_tup.path)
                self.pos[path_tup.pos_label] = pos_bin.pos


class TrodesPreprocessingDIOEpoch:
    def __init__(self, anim: TrodesAnimalInfo, date, epochtuple):

        self.anim = anim
        self.date = date
        self.epochtuple = epochtuple

        self.dio_paths = anim.preproc_dio_paths[(anim.preproc_dio_paths['date'] == date) &
                                                (anim.preproc_dio_paths['epoch'] == epochtuple)]

        self.dio = {}
        for path_tup in self.dio_paths.itertuples():
            if not pd.isnull(path_tup.channel):
                dio_list = self.dio.setdefault(path_tup.time_label, [])

                dio_bin = TrodesDIOBinaryLoader(path_tup.path)

                dio_bin.dio.columns = pd.MultiIndex.from_tuples([(path_tup.direction, int(path_tup.channel))],
                                                                names=['direction', 'channel'])

                dio_list.append(dio_bin.dio)


class TrodesPreprocessingToAnalysis:
    def __init__(self, anim: TrodesAnimalInfo):
        self.trodes_anim = anim

    def convert_lfp_day(self, date):
        self._convert_generic_day(
            date, self.trodes_anim.preproc_LFP_paths, 'lfp', self._write_lfp_epoch)

    def _write_lfp_epoch(self, date, epoch, hdf_store):
        lfp_epoch = TrodesPreprocessingLFPEpoch(self.trodes_anim, date, epoch)
        hdf_store['preprocessing/LFP/' +
                  'e{:02d}'.format(epoch[0]) + '/data'] = lfp_epoch.lfp

    def convert_spike_day(self, date, time_label='', parallel_instances=1):
        self._convert_generic_day(date, self.trodes_anim.preproc_spike_paths, 'spikewaves',
                                  functools.partial(self._write_spike_epoch,
                                                    time_label=time_label, parallel_instances=parallel_instances)
                                  )

    def _write_spike_epoch(self, date, epoch, hdf_store, time_label, parallel_instances=1):

        spike_epoch = TrodesPreprocessingSpikeEpoch(self.trodes_anim, date, epoch, time_label,
                                                    parallel_instances=parallel_instances)
        for ntrode, spike_ntrode in spike_epoch.spikes.items():
            hdf_store.put('preprocessing/EventWaveform/' + 'e{:02d}'.format(int(epoch[0])) +
                          '/t{:02d}'.format(int(ntrode)) + '/data',
                          spike_ntrode, expectedrows=len(spike_ntrode))

    def convert_pos_day(self, date):
        self._convert_generic_day(
            date, self.trodes_anim.preproc_dio_paths, 'rawpos', self._write_pos_epoch)

    def _write_pos_epoch(self, date, epoch, hdf_store):
        pos_epoch = TrodesPreprocessingPosEpoch(self.trodes_anim, date, epoch)
        for pos_label, pos_data in pos_epoch.pos.items():
            hdf_store.put('preprocessing/Position/' + 'e{:02d}'.format(int(epoch[0])) +
                          '/' + pos_label + '/data',
                          pos_data, expectedrows=len(pos_data))

    def convert_dio_day(self, date):
        self._convert_generic_day(
            date, self.trodes_anim.preproc_dio_paths, 'dio', self._write_dio_epoch)

    def _write_dio_epoch(self, date, epoch, hdf_store):
        dio_epoch = TrodesPreprocessingDIOEpoch(self.trodes_anim, date, epoch)
        # only take non adjusted dio
        dio_data = dio_epoch.dio['']
        for dio_chan_df in dio_data:
            hdf_store.put('preprocessing/BehavioralEvents/dio/' + 'e{:02d}'.format(int(epoch[0])) +
                          '/{:s}_{:02d}'.format(dio_chan_df.columns.get_level_values('direction')[0],
                                                int(dio_chan_df.columns.get_level_values('channel')[0])) +
                          '/data',
                          dio_chan_df)

    def _convert_generic_day(self, date, datatype_path_df, hdf_datatype_extension, write_epoch_func):

        if date not in datatype_path_df['date'].values:
            raise TrodesDataFormatError('Animal ({}), date ({}) does not have preprocessed {} data'.
                                        format(self.trodes_anim.anim_name, date, hdf_datatype_extension))

        if not os.path.exists(self.trodes_anim.get_analysis_dir()):
            os.mkdir(self.trodes_anim.get_analysis_dir())

        with pd.HDFStore(os.path.join(self.trodes_anim.get_analysis_dir(),
                                      TrodesPreprocessingToAnalysis.
                                      _assemble_analysis_base_name(date, self.trodes_anim.anim_name,
                                                                   hdf_datatype_extension))
                         ) as hdf_store:

            epochs = datatype_path_df[datatype_path_df['date']
                                      == date]['epoch'].unique()

            for epoch in epochs:
                write_epoch_func(date, epoch, hdf_store)

    @staticmethod
    def _assemble_analysis_base_name(date, anim_name, datatype):
        return date + '_' + anim_name + '_' + datatype + '.h5'


class ExtractRawTrodesData:

    def __init__(self, trodes_anim_info: TrodesAnimalInfo):
        self.trodes_anim_info = trodes_anim_info  # type: TrodesAnimalInfo

    def extract_lfp(self, dates, epochs,
                    export_args=('-highpass', '0', '-lowpass', '400', '-interp', '0', '-userefs', '0',
                                 '-outputrate', '1500'),
                    **kwargs):
        """
        Args:
            dates:
            epochs:
            export_args (Option[list]): Run exportLFP -h to see arguments
            **kwargs:

        Returns:

        """

        self._extract_rec_generic(export_cmd='exportLFP', export_dir_ext='LFP', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_mda(self, dates, epochs,
                    export_args=('-usespikefilters', '0',
                                 '-interp', '500', '-userefs', '1'),
                    **kwargs):
        self._extract_rec_generic(export_cmd='exportmda', export_dir_ext='mda', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_analog(self, dates, epochs, export_args=(), **kwargs):
        self._extract_rec_generic(export_cmd='exportanalog', export_dir_ext='analog', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_dio(self, dates, epochs, export_args=(), **kwargs):
        self._extract_rec_generic(export_cmd='exportdio', export_dir_ext='DIO', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_phy(self, dates, epochs,
                    export_args=('-usespikefilters', '0', '-interp', '1'),
                    **kwargs):
        self._extract_rec_generic(export_cmd='exportphy', export_dir_ext='phy', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_spikes(self, dates, epochs, export_args=(), **kwargs):
        self._extract_rec_generic(export_cmd='exportspikes', export_dir_ext='spikes', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def extract_time(self, dates, epochs, export_args=(), **kwargs):
        self._extract_rec_generic(export_cmd='exporttime', export_dir_ext='time', dates=dates, epochs=epochs,
                                  export_args=export_args, **kwargs)

    def prepare_trodescomments(self, dates, epochs, overwrite=False, use_folder_date=False, stop_error=False):
        for dir_date, epoch in itertools.product(dates, epochs):
            try:
                out_date_dir = self.trodes_anim_info.get_preprocessing_date_dir(
                    dir_date, stop_error=False)
                try:
                    epoch_comment_file = self.trodes_anim_info.get_raw_trodescomments_path(
                        dir_date, epoch)
                except KeyError as err:
                    raise TrodesDataFormatError(repr(err))

                file_parser = epoch_comment_file[0]
                file_path = epoch_comment_file[1]

                if use_folder_date:
                    out_base_date = dir_date
                else:
                    out_base_date = file_parser.date

                out_base_path = self._assemble_export_base_name(date=out_base_date,
                                                                anim_name=file_parser.name_str,
                                                                epochlist=file_parser.epochlist_str,
                                                                label=file_parser.label,
                                                                label_ext=file_parser.label_ext) + '.' + file_parser.ext

                online_comment_path = os.path.join(out_date_dir, out_base_path)

                if os.path.exists(out_base_path) and overwrite:
                    os.remove(out_base_path)

                try:
                    shutil.copyfile(file_path, online_comment_path)
                except FileExistsError:
                    pass

            except TrodesDataFormatError as err:
                if stop_error:
                    # exception should keep raised
                    raise
                else:
                    # exception should be converted to a warning
                    warnings.warn(repr(err) + ' (thrown from {}:{})'
                                  .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                          sys.exc_info()[2].tb_lineno),
                                  TrodesDataFormatWarning)

    def prepare_mountain_dir(self, dates, epochs, use_folder_date=False, stop_error=False):

        for dir_date, epoch in itertools.product(dates, epochs):
            try:
                out_date_dir = self.trodes_anim_info.get_preprocessing_date_dir(
                    dir_date, stop_error=False)
                try:
                    epoch_raw_file = self.trodes_anim_info.get_raw_rec_path(
                        dir_date, epoch)
                except KeyError:
                    raise TrodesDataFormatError('Rec: Date {} and epoch {} does not exist for animal {}.'.
                                                format(dir_date, epoch, self.trodes_anim_info.anim_name))

                file_parser = epoch_raw_file[0]
                file_path = epoch_raw_file[1]

                # create position dir
                if use_folder_date:
                    out_base_date = dir_date
                else:
                    out_base_date = file_parser.date

                out_base_dir_name = self._assemble_export_base_name(date=out_base_date,
                                                                    anim_name=file_parser.name_str,
                                                                    epochlist=file_parser.epochlist_str,
                                                                    label=file_parser.label,
                                                                    label_ext=file_parser.label_ext)

                out_dir_path = os.path.join(
                    out_date_dir, out_base_dir_name + '.mountain')
                if not os.path.exists(out_dir_path):
                    os.makedirs(out_dir_path)

            except TrodesDataFormatError as err:
                if stop_error:
                    # exception should keep raised
                    raise
                else:
                    # exception should be converted to a warning
                    warnings.warn(repr(err) + ' (thrown from {}:{})'
                                  .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                          sys.exc_info()[2].tb_lineno),
                                  TrodesDataFormatWarning)

    def prepare_pos_dir(self, dates, epochs, overwrite=False, use_folder_date=False, stop_error=False):
        for dir_date, epoch in itertools.product(dates, epochs):
            try:
                out_date_dir = self.trodes_anim_info.get_preprocessing_date_dir(
                    dir_date, stop_error=False)
                try:
                    h264_epoch_pathset = self.trodes_anim_info.get_raw_h264_paths(
                        dir_date, epoch)
                except KeyError:
                    raise TrodesDataFormatError('h264: Date {} and epoch {} does not exist for animal {}.'.
                                                format(dir_date, epoch, self.trodes_anim_info.anim_name))

                for label_ext, (h264_name_parser, h264_path) in h264_epoch_pathset.items():
                    # create position dir
                    if use_folder_date:
                        out_base_date = dir_date
                    else:
                        out_base_date = h264_name_parser.date

                    out_base_dir_name = self._assemble_export_base_name(date=out_base_date,
                                                                        anim_name=h264_name_parser.name_str,
                                                                        epochlist=h264_name_parser.epochlist_str,
                                                                        label=h264_name_parser.label,
                                                                        label_ext=h264_name_parser.label_ext)

                    out_dir_path = os.path.join(
                        out_date_dir, out_base_dir_name + '.pos')
                    if not os.path.exists(out_dir_path):
                        os.makedirs(out_dir_path)

                    # trying to move online position files over
                    try:
                        (raw_pos_filename_parser, raw_pos_path) = \
                            self.trodes_anim_info.get_raw_pos_path(date=dir_date,
                                                                   epoch=epoch,
                                                                   label_ext=label_ext)
                        online_pos_path = os.path.join(
                            out_dir_path, out_base_dir_name + '.pos_online.dat')

                        if os.path.exists(online_pos_path) and os.path.isfile(online_pos_path):
                            if overwrite:
                                os.remove(online_pos_path)
                        try:
                            shutil.copyfile(raw_pos_path, online_pos_path)
                        except FileExistsError:
                            pass

                    except KeyError as err:
                        # this file does not exist
                        warnings.warn(repr(err) + ' (thrown from {}:{})'
                                      .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                              sys.exc_info()[2].tb_lineno),
                                      TrodesDataFormatWarning)

                    try:
                        (raw_postime_filename_parser, raw_postime_path) = \
                            self.trodes_anim_info.get_raw_postime_path(date=dir_date,
                                                                       epoch=epoch,
                                                                       label_ext=label_ext)
                        postime_path = os.path.join(
                            out_dir_path, out_base_dir_name + '.pos_timestamps.dat')

                        if os.path.exists(postime_path) and os.path.isfile(postime_path):
                            if overwrite:
                                os.remove(postime_path)
                        try:
                            shutil.copyfile(raw_postime_path, postime_path)
                        except FileExistsError:
                            pass

                    except KeyError as err:
                        # this file does not exist
                        warnings.warn(repr(err) + ' (thrown from {}:{})'
                                      .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                              sys.exc_info()[2].tb_lineno),
                                      TrodesDataFormatWarning)

                    try:
                        (raw_poshwframecount_filename_parser, raw_poshwframecount_path) = \
                            self.trodes_anim_info.get_raw_poshwframecount_path(date=dir_date,
                                                                               epoch=epoch,
                                                                               label_ext=label_ext + '.videoTimeStamps')
                        poshwframecount_path = os.path.join(out_dir_path,
                                                            out_base_dir_name + '.pos_cameraHWFrameCount.dat')

                        if os.path.exists(poshwframecount_path) and os.path.isfile(poshwframecount_path):
                            if overwrite:
                                os.remove(poshwframecount_path)
                        try:
                            shutil.copyfile(
                                raw_poshwframecount_path, poshwframecount_path)
                        except FileExistsError:
                            pass

                    except KeyError as err:
                        # this file does not exist
                        warnings.warn(repr(err) + ' (thrown from {}:{})'
                                      .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                              sys.exc_info()[2].tb_lineno),
                                      TrodesDataFormatWarning)

            except TrodesDataFormatError as err:
                if stop_error:
                    # exception should keep raised
                    raise
                else:
                    # exception should be converted to a warning
                    warnings.warn(repr(err) + ' (thrown from {}:{})'
                                  .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                          sys.exc_info()[2].tb_lineno),
                                  TrodesDataFormatWarning)

    def _extract_rec_generic(self, export_cmd, export_dir_ext,
                             dates, epochs, export_args=(), overwrite=False, stop_error=False,
                             use_folder_date=False, parallel_instances=1, use_day_config=True):
        """
        Args:
            export_cmd (str):
            export_dir_ext (str):
            dates (list):
            epochs (list):
            export_args (Optional[list]):
            overwrite (Optional[bool]):
            stop_error (Optional[bool]): If True then raise exceptions if a date and epoch combo does not exist or
                if trying to extract over an existing folder when overwrite is off.  If False then instead of raising
                exceptions, warnings are issued.
            parallel_instances (Optional[int]):

        """

        subprocess_pool = {}
        terminated_processes = {}

        next_cmd_id = 0

        file_paths_parsed = set()
        for dir_date, epoch in itertools.product(dates, epochs):
            try:
                out_date_dir = self.trodes_anim_info.get_preprocessing_date_dir(
                    dir_date, stop_error=False)

                try:
                    epoch_raw_file = self.trodes_anim_info.get_raw_rec_path(
                        dir_date, epoch)
                except KeyError:
                    raise TrodesDataFormatError('Rec: Date {} and epoch {} does not exist for animal {}.'.
                                                format(dir_date, epoch, self.trodes_anim_info.anim_name))

                file_parser = epoch_raw_file[0]
                file_path = epoch_raw_file[1]

                if file_path in file_paths_parsed:
                    # skip this file because we already tried to parse it
                    pass
                else:
                    # immediately add path to parsed list to make sure we don't try to parse it again
                    file_paths_parsed.add(file_path)

                    if file_parser.date != dir_date:
                        if use_folder_date:
                            warnings.warn(('For rec file ({}) the date field does not match '
                                           'the folder date ({}). Forcing file to use folder date').
                                          format(file_parser.filename, dir_date), TrodesDataFormatWarning)
                        else:
                            warnings.warn(('For rec file ({}) the date field does not match '
                                           'the folder date ({}). This should be fixed or could have '
                                           'unintended parsing consequences. Will proceed by maintaining '
                                           'folder date and using rec file date in extracted files.').
                                          format(file_parser.filename, dir_date), TrodesDataFormatWarning)

                    if use_folder_date:
                        out_base_date = dir_date
                    else:
                        out_base_date = file_parser.date
                    out_base_filename = self._assemble_export_base_name(date=out_base_date,
                                                                        anim_name=file_parser.name_str,
                                                                        epochlist=file_parser.epochlist_str,
                                                                        label=file_parser.label,
                                                                        label_ext=file_parser.label_ext)

                    out_epoch_dir = os.path.join(
                        out_date_dir, out_base_filename + '.' + export_dir_ext)
                    if os.path.exists(out_epoch_dir):
                        if overwrite:
                            shutil.rmtree(out_epoch_dir)
                        else:
                            raise TrodesDataFormatError(('skipping rec file {} for extracting, '
                                                         'folder {} already exists and overwrite=False.').
                                                        format(file_parser.filename, out_epoch_dir))

                    os.makedirs(out_epoch_dir)

                    # check if using external config
                    if use_day_config:
                        try:
                            external_config_filename = self.trodes_anim_info.get_date_trodesconf(
                                dir_date)
                        except KeyError:
                            # not using external config
                            external_config_filename = None
                    else:
                        external_config_filename = None

                    if external_config_filename is None:
                        export_call = [export_cmd, '-rec', file_path, '-outputdirectory', out_date_dir,
                                       '-output', out_base_filename]
                    else:
                        export_call = [export_cmd, '-rec', file_path, '-outputdirectory', out_date_dir,
                                       '-output', out_base_filename, '-reconfig', external_config_filename]

                    export_call.extend(export_args)

                    # if pool slots are full, wait for one subprocess to terminate
                    just_terminated = self._wait_subprocess_pool(subprocess_pool=subprocess_pool,
                                                                 wait_pool_size=parallel_instances - 1)
                    terminated_processes.update(just_terminated)

                    # create log file for each run of the export command
                    out_cmd_log_filename = os.path.join(
                        out_epoch_dir, out_base_filename + '.' + export_cmd + '.log')
                    out_cmd_log_file = open(out_cmd_log_filename, 'w')
                    # prepend the call command and argument to the log file
                    out_cmd_log_file.write(' '.join(export_call))
                    out_cmd_log_file.write('\n')

                    # create new export command subprocess
                    print('(ID: {}) Running {} on animal {} date {} epoch {}'.
                          format(next_cmd_id, export_cmd, file_parser.name_str,
                                 out_base_date, file_parser.epochlist_str))
                    print('(ID: {}) Full command: {}'.format(
                        next_cmd_id, export_call))
                    #subprocess_pool[next_cmd_id] = subprocess.Popen(export_call)
                    subprocess_pool[next_cmd_id] = (subprocess.Popen(export_call,
                                                                     stdout=out_cmd_log_file,
                                                                     stderr=out_cmd_log_file),
                                                    out_cmd_log_filename)
                    next_cmd_id += 1

            except TrodesDataFormatError as err:
                if stop_error:
                    # exception should keep raised
                    raise
                else:
                    # exception should be converted to a warning
                    warnings.warn(repr(err) + ' (thrown from {}:{})'
                                  .format(sys.exc_info()[2].tb_frame.f_code.co_filename,
                                          sys.exc_info()[2].tb_lineno),
                                  TrodesDataFormatWarning)

        # wait for all commands to finish
        just_terminated = self._wait_subprocess_pool(
            subprocess_pool, wait_pool_size=0)
        terminated_processes.update(just_terminated)

        for cmd_key, (extract_proc, cmd_log_file) in terminated_processes.items():
            if extract_proc.poll() != 0:
                warnings.warn('Running export command ({}) failed with return code {}'.
                              format(extract_proc.args, extract_proc.poll()), TrodesDataFormatWarning)

    @staticmethod
    def _assemble_export_base_name(date, anim_name, epochlist, label, label_ext):
        out_base_filename = date + '_' + anim_name + '_' + epochlist
        if label != '':
            out_base_filename += '_' + label
        if label_ext != '':
            out_base_filename += '.' + label_ext

        return out_base_filename

    @staticmethod
    def _wait_subprocess_pool(subprocess_pool, wait_pool_size):
        terminated_processes = {}
        while len(subprocess_pool) > wait_pool_size:
            time.sleep(1.0)
            for cmd_key, (extract_proc, cmd_log_filename) in list(subprocess_pool.items()):
                return_code = extract_proc.poll()
                if return_code is not None:
                    del subprocess_pool[cmd_key]
                    terminated_processes[cmd_key] = (
                        extract_proc, cmd_log_filename)
                    print('(ID: {}) Done running {}'.format(
                        cmd_key, extract_proc.args))
                    # print log file
                    with open(cmd_log_filename, 'r') as f:
                        for line in f:
                            print('(ID: {}) '.format(cmd_key) + line, end='')

        return terminated_processes
