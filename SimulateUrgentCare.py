import ModelEntities as Cls
import InputData as D
import ModelParameters as P
import SimPy.SamplePathClasses as Path
import SimPy.FigureSupport as Fig

# create an urgent care
myUrgentCare = Cls.UrgentCare(id=1, parameters=P.Parameters())

# simulate the urgent care
myUrgentCare.simulate(sim_duration=D.SIM_DURATION)

# sample path for patients waiting
Path.graph_sample_path(
    sample_path=myUrgentCare.simOutputs.nPatientsWaiting,
    title='Patients Waiting',
    x_label='Simulation time (hours)',
)
# sample path for patients in the system
Path.graph_sample_path(
    sample_path=myUrgentCare.simOutputs.nPatientInSystem,
    title='Patients In System',
    x_label='Simulation time (hours)',
)
# sample path for exam rooms busy
Path.graph_sample_path(
    sample_path=myUrgentCare.simOutputs.nExamRoomBusy,
    title='Exam Rooms Busy',
    x_label='Simulation time (hours)'
)
Fig.graph_histogram(
    data=myUrgentCare.simOutputs.patientTimeInSystem,
    title='Patients Time in System',
    x_label='Hours',
)
Fig.graph_histogram(
    data=myUrgentCare.simOutputs.patientTimeInWaitingRoom,
    title='Patients Time in Waiting Room',
    x_label='Hours',
)

# performance statistics
print('Patients arrived:', myUrgentCare.simOutputs.nPatientsArrived)
print('Patients served:', myUrgentCare.simOutputs.nPatientServed)
print('Average patient time in system:', myUrgentCare.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', myUrgentCare.simOutputs.get_ave_patient_waiting_time())

print('Maximum number of patients in the waiting room:', myUrgentCare.simOutputs.nPatientsWaiting.stat.get_max())
print('Average number of patients in the waiting room:', myUrgentCare.simOutputs.nPatientsWaiting.stat.get_mean())
print('Average number of patients in the system:', myUrgentCare.simOutputs.nPatientInSystem.stat.get_mean())
print('Utilization of exam rooms:', myUrgentCare.simOutputs.nExamRoomBusy.stat.get_mean())

# print trace
myUrgentCare.print_trace()
