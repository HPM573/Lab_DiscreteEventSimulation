
# trace
TRACE_ON = True        # Set to true to trace a simulation replication
DECI = 5                # the decimal point to round the numbers to in the trace file

# simulation settings
SIM_DURATION = 100000   # (hours) a large number to make sure the simulation will be terminated eventually but
                        # the simulation continues as long as there is a patient in the urgent care.
HOURS_OPEN = 20                 # hours the urgent cares open
N_EXAM_ROOMS = 2                # number of exam rooms
MEAN_ARRIVAL_TIME = 5/60        # mean patients inter-arrival time (hours)
MEAN_EXAM_DURATION = 8/60       # mean of exam duration (hours)
