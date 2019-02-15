import SimPy.SamplePathClasses as Path


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, sim_cal):
        """
        :param sim_cal: simulation calendar
        """

        self.simCal = sim_cal           # simulation calendar
        self.nPatientsArrived = 0       # number of patients arrived
        self.nPatientServed = 0         # number of patients served
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInWaitingRoom = []  # observations on patients time in the waiting room

        # sample path for the patients waiting
        self.nPatientsWaiting = Path.PrevalencePathRealTimeUpdate(
            name='Number of patients waiting', initial_size=0)

        # sample path for the patients in system
        self.nPatientInSystem = Path.PrevalencePathRealTimeUpdate(
            name='Number of patients in the urgent care', initial_size=0)

        # sample path for the number of exam rooms busy
        self.nExamRoomBusy = Path.PrevalencePathRealTimeUpdate(
            name='Number of exam rooms busy', initial_size=0
        )

    def collect_patient_arrival(self, patient):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        :param time: the arrival time
        """

        # increment the number of patients arrived
        self.nPatientsArrived += 1

        # patients in the system
        self.nPatientInSystem.record(time=self.simCal.time, increment=+1)

        # store arrival time of this patient
        patient.tArrived = self.simCal.time

    def collect_patient_join_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room
        :param patient: the patient who is joining the waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaiting.record(time=self.simCal.time, increment=1)

    def collect_patient_leave_waiting_room(self, patient):
        """ collects statistics when a patient leave the waiting room
        :param patient: the patient who is leave the waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaiting.record(time=self.simCal.time, increment=-1)

    def collect_patient_departure(self, patient):
        """ collects statistics for a departing patient
        :param patient: the departing patient
        """

        self.nPatientServed += 1
        self.nPatientInSystem.record(time=self.simCal.time, increment=-1)
        self.nExamRoomBusy.record(time=self.simCal.time, increment=-1)
        self.patientTimeInSystem.append(self.simCal.time-patient.tArrived)
        self.patientTimeInWaitingRoom.append(patient.tLeftWaitingRoom-patient.tJoinedWaitingRoom)

    def collect_start_exam(self):
        """ collects statistics for a patient who just started the exam """

        self.nExamRoomBusy.record(time=self.simCal.time, increment=+1)

    def collect_end_of_sim_stat(self):
        """
        collects the performance statistics at the end of this replication of the urgent care simulation
        """

        # update sample paths
        self.nPatientsWaiting.record(time=self.simCal.time, increment=0)
        self.nPatientInSystem.record(time=self.simCal.time, increment=0)
        self.nExamRoomBusy.record(time=self.simCal.time, increment=0)

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
