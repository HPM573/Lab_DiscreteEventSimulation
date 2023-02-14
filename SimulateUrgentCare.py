import deampy.plots.histogram as hist
import deampy.plots.sample_paths as path

import DESInputData as D
import ModelParameters as P
import UrgentCareModel as M

# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

# sample path for patients waiting
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaiting,
    title='Patients Waiting',
    x_label='Simulation time (hours)',
)
# sample path for patients in the system
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientInSystem,
    title='Patients In System',
    x_label='Simulation time (hours)',
)
# sample path for physician utilization
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPhysiciansBusy,
    title='Physician Utilization',
    x_label='Simulation time (hours)'
)
hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInSystem,
    title='Patients Time in System',
    x_label='Hours',
    #bin_width=.2
)
hist.plot_histogram(
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
print('Average utilization of physicians (%):',
      100 * urgentCareModel.simOutputs.nPhysiciansBusy.stat.get_mean() / D.N_PHYSICIANS)

