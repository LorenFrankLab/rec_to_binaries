from read_binaries import readTrodesExtractedDataFile, write_trodes_extracted_datafile

import numpy as np

def add_system_time_to_file(continuous_time_file, new_file_name):
	cont_time = readTrodesExtractedDataFile(continuous_time_file)
	cont_time['data'] = create_and_add_system_timepoints(cont_time)
	if 'fields' in cont_time:
		cont_time['fields'] = '<trodestime uint32><systime int64>'
	else:
		cont_time['Fields'] = '<trodestime uint32><systime int64>'
	write_trodes_extracted_datafile(new_file_name, cont_time)

def create_and_add_system_timepoints(cont_time):
	# Assumptions: 'clockrate' is in Hz; 'system_time_at_creation' is taken to the millisecond

	if 'clockrate' in cont_time:
		nanosec_per_sample = int((1/int(cont_time['clockrate']))* (1e9))
	else:
		nanosec_per_sample = int((1/int(cont_time['Clockrate']))* (1e9))

	sys_time = np.zeros(np.shape(cont_time['data'])).astype('int64')

	if 'timestamp_at_creation' in cont_time:
		interval = (cont_time['data'][0][0] - int(cont_time['timestamp_at_creation'])) * nanosec_per_sample
	else:
		interval = (cont_time['data'][0][0] - int(cont_time['Timestamp_at_creation'])) * nanosec_per_sample

	if 'system_time_at_creation' in cont_time:
		sys_time[0] = (interval + (int(cont_time['system_time_at_creation']) * (1e6))).astype(int)
	else:
		sys_time[0] = (interval + (int(cont_time['System_time_at_creation']) * (1e6))).astype(int)

	for i in range(1,np.size(sys_time)):
	    trodes_interval = cont_time['data'][i][0] - cont_time['data'][i-1][0]
	    
	    #conditionals account for rounding and skipped trodes samples in nanoseconds
	    if (trodes_interval%3==0):
	        sys_interval = int(trodes_interval * nanosec_per_sample) + int(trodes_interval/3)
	    elif (i%3==0):
	        sys_interval = int(trodes_interval * nanosec_per_sample) + 1
	    else:
	        sys_interval = int(trodes_interval * nanosec_per_sample)
	    
	    sys_time[i] = sys_interval + sys_time[i-1]

    return package_sys_time_with_trodes_time(sys_time, cont_time)


def package_sys_time_with_trodes_time(sys_time, cont_time):
	# data type copied from current continuoustime.dat files
	dt = np.dtype([('trodestime', np.uint32), ('systime', np.int64)])

	data = [0] * np.size(sys_time)

	for i in range(0,np.size(data)):
	    data[i] = (cont_time['data'][i][0], sys_time[i])

	packaged_data = np.array(data, dtype=dt)

	return packaged_data
