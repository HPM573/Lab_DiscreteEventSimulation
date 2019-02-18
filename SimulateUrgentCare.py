import ModelEntities as Cls
import InputData as D
import ModelParameters as P
import SimPy.SamplePathClasses as Path

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

# outputs
print('Patients arrived:', myUrgentCare.simOutputs.nPatientsArrived)
print('Patients served:', myUrgentCare.simOutputs.nPatientServed)
print('Average patient time in system:', myUrgentCare.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', myUrgentCare.simOutputs.get_ave_patient_waiting_time())

# print statistics
myUrgentCare.print_trace()
