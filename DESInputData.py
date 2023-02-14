
# trace
TRACE_ON = True        # Set to true to trace a simulation replication
DECI = 5                # the decimal point to round the numbers to in the trace file

# simulation settings
SIM_DURATION = 100000   # (hours) a large number to make sure the simulation will be terminated eventually but
                        # the simulation continues as long as there is a patient in the urgent care.
HOURS_OPEN = 30*24                 # hours the urgent cares open
N_PHYSICIANS = 20                # number of physicians
MEAN_ARRIVAL_TIME = 20/60/20        # mean patients inter-arrival time (hours)
MEAN_EXAM_DURATION = 20/60       # mean of exam duration (hours)
