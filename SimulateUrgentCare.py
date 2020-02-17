import UrgentCareModel as M
import InputData as D
import ModelParameters as P
import SimPy.Plots.Histogram as Hist
import SimPy.Plots.SamplePaths as Path

# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

# report number of patients arrived and served
print('Patients arrived:', urgentCareModel.urgentCare.nPatientsArrived)
print('Patients served:', urgentCareModel.urgentCare.nPatientsServed)
