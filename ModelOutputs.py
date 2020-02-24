import SimPy.SamplePathClasses as Path
import SimPy.FormatFunctions as F
import InputData as D


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, sim_cal, warm_up_period, trace_on=False):
        """
        :param sim_cal: simulation calendar
        :param warm_up_period: warm up period (hours)
        :param trace_on: set to True to report patient summary
        """

        self.simCal = sim_cal           # simulation calendar (to know the current time)
        self.warmUpPeriod = warm_up_period     # warm up period
        self.traceOn = trace_on         # if should prepare patient summary report
        self.nPatientsArrived = 0       # number of patients arrived
        self.nPatientsServed = 0         # number of patients served
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInWaitingRoom = []  # observations on patients time in the waiting room

        self.patientSummary = []    # id, tArrived, tLeft, duration waited, duration in the system
        if self.traceOn:
            self.patientSummary.append(
                ['Patient', 'Time Arrived', 'Time Left', 'Time Waited', 'Time In the System'])

        # sample path for the patients waiting
        self.nPatientsWaiting = Path.PrevalenceSamplePath(
            name='Number of patients waiting', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the patients in system
        self.nPatientInSystem = Path.PrevalenceSamplePath(
            name='Number of patients in the urgent care', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the number of exam rooms busy
        self.nExamRoomBusy = Path.PrevalenceSamplePath(
            name='Number of exam rooms busy', initial_size=0, warm_up_period=warm_up_period)

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

        time_waiting = patient.tLeftWaitingRoom-patient.tJoinedWaitingRoom
        time_in_system = self.simCal.time-patient.tArrived

        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=-1)
        self.nExamRoomBusy.record_increment(time=self.simCal.time, increment=-1)

        if self.simCal.time > self.warmUpPeriod:
            self.nPatientsServed += 1
            self.patientTimeInWaitingRoom.append(time_waiting)
            self.patientTimeInSystem.append(time_in_system)

        # build the patient summary
        if self.traceOn:
            self.patientSummary.append([
                str(patient),  # name
                F.format_number(patient.tArrived, deci=D.DECI),  # time arrived
                F.format_number(self.simCal.time, deci=D.DECI),  # time left
                F.format_number(time_waiting, deci=D.DECI),  # time waiting
                F.format_number(time_in_system, deci=D.DECI)]  # time in the system
            )

    def collect_patient_starting_exam(self):
        """ collects statistics for a patient who just started the exam """

        self.nExamRoomBusy.record_increment(time=self.simCal.time, increment=+1)

    def collect_end_of_simulation(self):
        """
        collects the performance statistics at the end of the simulation
        """

        # update sample paths
        self.nPatientsWaiting.close(time=self.simCal.time)
        self.nPatientInSystem.close(time=self.simCal.time)
        self.nExamRoomBusy.close(time=self.simCal.time)

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
