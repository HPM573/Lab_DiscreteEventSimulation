import SimPy.SamplePathClasses as Path


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self):

        # performance statistics collectors
        self.nPatientsArrived = 0
        self.nPatientServed = 0
        self.nPatientInSystem = Path.PrevalencePathRealTimeUpdate(
            name='Number of patients in the urgent care', initial_size=0)
        self.nExamRoomBusy = Path.PrevalencePathRealTimeUpdate(
            name='Number of exam rooms busy', initial_size=0
        )
        self.patientTimeInSystem = []
        self.patientTimeInWaitingRoom = []

    def process_patient_arrival(self, patient, time):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        :param time: the arrival time
        """
        self.nPatientsArrived += 1
        self.nPatientInSystem.record(time=time, increment=+1)
        # store the patient arrival time
        patient.tArrived = time

    def process_patient_departure(self, patient, time):
        """ collects statistics for a departing patient
        :param patient: the departing patient
        :param time: the departure time
        """
        self.nPatientServed += 1
        self.nPatientInSystem.record(time=time, increment=-1)
        self.nExamRoomBusy.record(time=time, increment=-1)
        self.patientTimeInSystem.append(time-patient.tArrived)
        self.patientTimeInWaitingRoom.append(patient.tLeftWaitingRoom-patient.tJoinedWaitingRoom)

    def process_start_exam(self, time):
        """ collects statistics for a patient who just started the exam
        :param time: the time when the patient starts the exam
        """
        self.nExamRoomBusy.record(time=time, increment=+1)

    def collect_end_of_sim_stat(self, time):
        """
        collects the performance statistics at the end of this replication of the urgent care simulation
        :param time: simulation time
        """

        # update sample paths
        self.nPatientInSystem.record(time=time, increment=0)
        self.nExamRoomBusy.record(time=time, increment=0)

    def get_ave_patient_time_in_system(self):
        """
        :return: average patient time in system
        """

        return sum(self.patientTimeInSystem)/len(self.patientTimeInSystem)

    def get_ave_patient_waiting_time(self):
        """
        :return: average patient waiting time
        """

        return sum(self.patientTimeInWaitingRoom) / len(self.patientTimeInWaitingRoom)
