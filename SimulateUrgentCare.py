import UrgentCareModel as M
import InputData as D
import ModelParameters as P
import SimPy.Plots.Histogram as Hist
import SimPy.Plots.SamplePaths as Path

# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

# sample path for patients waiting
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaiting,
    title='Patients Waiting',
    x_label='Simulation time (hours)',
)
# sample path for patients in the system
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientInSystem,
    title='Patients In System',
    x_label='Simulation time (hours)',
)
# sample path for exam rooms busy
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nExamRoomBusy,
    title='Exam Rooms Busy',
    x_label='Simulation time (hours)'
)
Hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInSystem,
    title='Patients Time in System',
    x_label='Hours',
    #bin_width=.2
)
Hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInWaitingRoom,
    title='Patients Time in Waiting Room',
    x_label='Hours',
    #bin_width=0.2
)

# performance statistics
print('Patients arrived:', urgentCareModel.simOutputs.nPatientsArrived)
print('Patients served:', urgentCareModel.simOutputs.nPatientsServed)
print('Average patient time in system:', urgentCareModel.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', urgentCareModel.simOutputs.get_ave_patient_waiting_time())

print('Maximum number of patients in the waiting room:', urgentCareModel.simOutputs.nPatientsWaiting.stat.get_max())
print('Average number of patients in the waiting room:', urgentCareModel.simOutputs.nPatientsWaiting.stat.get_mean())
print('Average number of patients in the system:', urgentCareModel.simOutputs.nPatientInSystem.stat.get_mean())
print('Average utilization of exam rooms (%):',
      100*urgentCareModel.simOutputs.nExamRoomBusy.stat.get_mean()/D.N_EXAM_ROOMS)

# print trace
urgentCareModel.print_trace()
