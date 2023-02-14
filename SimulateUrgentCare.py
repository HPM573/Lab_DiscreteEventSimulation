import DESInputData as D
import ModelParameters as P
import UrgentCareModel as M

# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

# report number of patients arrived and served
print('Patients arrived:', urgentCareModel.urgentCare.nPatientsArrived)
print('Patients served:', urgentCareModel.urgentCare.nPatientsServed)
