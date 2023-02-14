from deampy.sample_path import PrevalenceSamplePath


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, sim_cal, warm_up_period):
        """
        :param sim_cal: simulation calendar
        :param warm_up_period: warm up period
        """

        self.simCal = sim_cal           # simulation calendar (to know the current time)
        self.warmUpPeriod = warm_up_period  # warm up period
        self.nPatientsArrived = 0       # number of patients arrived
        self.nPatientsServed = 0         # number of patients served
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInWaitingRoom = []  # observations on patients time in the waiting room

        self.patientSummary = []    # id, tArrived, tLeft, duration waited, duration in the system

        # sample path for the patients waiting
        self.nPatientsWaiting = PrevalenceSamplePath(
            name='Number of patients waiting', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the patients in system
        self.nPatientInSystem = PrevalenceSamplePath(
            name='Number of patients in the urgent care', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the number of physicians busy
        self.nPhysiciansBusy = PrevalenceSamplePath(
            name='Number of physicians busy', initial_size=0, warm_up_period=warm_up_period)

    def collect_patient_arrival(self, patient):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        """

        # increment the number of patients arrived
        if self.simCal.time > self.warmUpPeriod:
            self.nPatientsArrived += 1

        # update the sample path of patients in the system
        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=+1)

        # store arrival time of this patient
        patient.tArrived = self.simCal.time

    def collect_patient_joining_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room
        :param patient: the patient who is joining the waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.time

        # update the sample path of patients waiting
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_leaving_waiting_room(self, patient):
        """ collects statistics when a patient leave the waiting room
        :param patient: the patient who is leave the waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_departure(self, patient):
        """ collects statistics for a departing patient
        :param patient: the departing patient
        """

        # if patient never joined the waiting room, the waiting time is 0
        if patient.tJoinedWaitingRoom is None:
            time_waiting = 0
        else:
            time_waiting = patient.tLeftWaitingRoom - patient.tJoinedWaitingRoom

        time_in_system = self.simCal.time - patient.tArrived

        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=-1)
        self.nPhysiciansBusy.record_increment(time=self.simCal.time, increment=-1)

        if self.simCal.time > self.warmUpPeriod:
            self.nPatientsServed += 1
            self.patientTimeInWaitingRoom.append(time_waiting)
            self.patientTimeInSystem.append(time_in_system)

    def collect_patient_starting_exam(self):
        """ collects statistics for a patient who just started the exam """

        self.nPhysiciansBusy.record_increment(time=self.simCal.time, increment=+1)

    def collect_end_of_simulation(self):
        """
        collects the performance statistics at the end of the simulation
        """

        # update sample paths
        self.nPatientsWaiting.close(time=self.simCal.time)
        self.nPatientInSystem.close(time=self.simCal.time)
        self.nPhysiciansBusy.close(time=self.simCal.time)

    def get_ave_patient_time_in_system(self):
        """
        :return: average patient time in system
        """

        return sum(self.patientTimeInSystem)/len(self.patientTimeInSystem)

    def get_ave_patient_waiting_time(self):
        """
        :return: average patient waiting time
        """

        return sum(self.patientTimeInWaitingRoom)/len(self.patientTimeInWaitingRoom)
