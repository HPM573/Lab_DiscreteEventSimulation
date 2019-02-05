import SimPy.DiscreteEventClasses as SimCls
import UrgentCareEvents as Events
import SimPy.RandomVariantGenerators as RVGs
import SimPy.SamplePathClasses as Path
import InputData as D


class Patient:
    def __init__(self, id):
        """ create a patient
        :param id: (integer) patient ID
        """
        self.id = id
        self.tArrived = 0               # time the patient arrived
        self.tJoinedWaitingRoom = 0     # time the patient joined the waiting room
        self.tLeftWaitingRoom = 0       # time the patient left the waiting room

    def __str__(self):
        return "Patient " + str(self.id)


class WaitingRoom:
    def __init__(self, sim_cal, trace):
        """ create a waiting room
        :param sim_cal: simulation calendar
        :param trace: simulation trace
        """
        self.patients = []  # list to store patients waiting
        self.simCal = sim_cal
        self.trace = trace
        # statistics
        self.numPatientsWaiting = Stat.ContinuousTimeStat('Number of patients waiting', 0)

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """
        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.get_current_time()
        # add the patient to the list of patients waiting
        self.patients.append(patient)
        # update statistics
        self.numPatientsWaiting.record(self.simCal.get_current_time(), +1)
        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room. Number waiting = ' + str(len(self.patients)) + '.')

    def next_patient(self):
        """
        :returns: the next patient in line
        """
        # update performance statistics
        self.patients[0].tLeftWaitingRoom = self.simCal.get_current_time()
        self.numPatientsWaiting.record(self.simCal.get_current_time(), -1)

        # trace
        self.trace.add_message(
            str(self.patients[0]) + ' leaves the waiting room. Number waiting = ' + str(len(self.patients) - 1) + '.')
        # pop the patient
        return self.patients.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patients)


class ExamRoom:
    def __init__(self, idn, urgent_care, service_time_dist):
        """ create an exam room
        :param idn: (integer) the exam room ID
        :param urgent_care: the urgent care object
        :param service_time_dist: distribution of service time in this exam room
        """
        self.ID = idn
        self.urgentCare = urgent_care
        self.rnd = urgent_care.rnd
        self.serviceTimeDist = service_time_dist
        self.isBusy = False
        self.patientBeingServed = None

    def __str__(self):
        """ :returns (string) the exam room number """
        return "Exam Room " + str(self.ID)

    def exam(self, patient):
        """ starts examining on the passed patient
        :param patient: a patient
        """
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.urgentCare.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # find the exam completion time
        exam_completion_time = self.urgentCare.simCal.get_current_time() + self.serviceTimeDist.sample(self.rnd)

        # schedule the end of exam
        self.urgentCare.simCal.add_event(
            Events.EndOfExam(exam_completion_time, self, self.urgentCare)
        )

    def remove_patient(self):
        """ :returns the patient that was being served in this exam room"""

        self.isBusy = False
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # trace
        self.urgentCare.trace.add_message(str(returned_patient) + ' leaves ' + str(self) + '.')

        return returned_patient


class UrgentCare:
    def __init__(self, idn):
        """ creates an urgent care
        :param idn: (integer) ID of this urgent care
        :parameter: (Parameters) parameters of this urgent care
        """

        self.id = idn                   # urgent care id
        self.ifOpen = True              # if the urgent care is open and admitting new patients
        self.rnd = RVGs.RNG(seed=idn)    # random number generator
        self.params = Parameters()        # parameters of this urgent care

        # model entities
        self.patients = []          # list of patients
        self.waitingRoom = None     # the waiting room object
        self.examRooms = []         # list of exam rooms

        # set up the simulation calendar
        self.simCal = SimCls.SimulationCalendar()

        # set up trace
        self.trace = SimCls.Trace(self.simCal, D.TRACE_ON, D.DECI)

        # set up model entities
        self.__setup_entities()

        # initialize performance statistics
        self.simOutputs = SimOutputs(self)

    def __setup_entities(self):
        """ sets up the urgent care entities"""

        # create a waiting room
        self.waitingRoom = WaitingRoom(self.simCal, self.trace)

        # create exam rooms
        for i in range(0, self.params.nExamRooms):
            self.examRooms.append(
                ExamRoom(idn=i,
                         urgent_care=self,
                         service_time_dist=self.params.examTimeDist)
            )

    def __initialize(self):
        """ initialize simulating the urgent care """

        # reset the simulation calendar
        self.simCal.clear_calendar()

        # find the arrival time of the first patient
        arrival_time = self.params.arrivalTimeDist.sample(self.rnd)

        # schedule the closing event
        self.simCal.add_event(
            Events.CloseUrgentCare(time=self.params.hoursOpen, urgent_care=self)
        )

        # schedule the arrival of the first patient
        self.simCal.add_event(
            Events.Arrival(time=arrival_time, patient=Patient(0), urgent_care=self)
        )

    def simulate(self, sim_duration):
        """ simulate the urgent care
        :param sim_duration: duration of simulation
         """

        # initialize the simulation
        self.__initialize()

        # while there is an event scheduled in the simulation calendar
        while self.simCal.n_events() > 0 and self.simCal.get_current_time() <= sim_duration:
            self.simCal.get_next_event().process()

        # collect the end of simulation statistics
        self.simOutputs.collect_end_of_sim_stat()

        return self.simOutputs

    def print_trace(self):
        """ outputs trace """
        self.trace.print_trace("Replication" + str(self.id) + ".txt", '../Labs_DiscreteEventSimulation/Trace')

    def receive_patient(self, patient):
        """ receives a new patient
        :param patient: the new patient
        """

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            self.trace.add_message('Urgent care closed. '+str(patient)+' does not get admitted.')
            return

        # add the new patient to the list of patients
        self.patients.append(patient)

        # collect statistics
        self.simOutputs.process_patient_arrival(patient, self.simCal.get_current_time())

        # find an idle exam room
        idle_room_found = False
        i_room = 0
        while (not idle_room_found) and i_room < len(self.examRooms):
            if not self.examRooms[i_room].isBusy:
                # send the last patient to this exam room
                self.examRooms[i_room].exam(self.patients[-1])
                idle_room_found = True
                # collect statistics
                self.simOutputs.process_start_exam(patient, self.simCal.get_current_time())
            else:
                i_room += 1

        # if no idle room was found
        if not idle_room_found:
            # add the patient to the waiting room
            self.waitingRoom.add_patient(self.patients[-1])

        # find the arrival time of the next patient
        next_arrival_time = self.simCal.get_current_time() + self.params.arrivalTimeDist.sample(self.rnd)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            Events.Arrival(
                time=next_arrival_time,
                patient=Patient(patient.ID + 1),
                urgent_care=self
            )
        )

    def process_end_of_exam(self, exam_room):
        """ processes the end of exam in the specified exam room
        :param exam_room: the exam room where the service is ended
        """
        # get the patient who is about to be discharged
        discharged_patient = exam_room.remove_patient()
        # collect statistics
        self.simOutputs.process_patient_departure(discharged_patient, self.simCal.get_current_time())

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # start serving the next patient in line
            exam_room.exam(self.waitingRoom.next_patient())
            # collect statistics
            self.simOutputs.process_start_exam(exam_room.patientBeingServed, self.simCal.get_current_time())


class Parameters:
    # class to contain the parameters of the urgent care model
    def __init__(self):
        self.hoursOpen = D.HOURS_OPEN
        self.nExamRooms = D.N_EXAM_ROOMS
        self.arrivalTimeDist = RVGs.Exponential(scale=D.MEAN_ARRIVAL_TIME)
        self.examTimeDist = RVGs.Exponential(scale=D.MEAN_EXAM_DURATION)


class SamplePaths:
    # store simulation sample paths (e.g. the number of patients in system over time)

    def __init__(self, itr):
        self.nOfPatients = Path.SamplePathRealTimeUpdate('Number of Patients', itr, 0)
        self.utilization = Path.SamplePathRealTimeUpdate('Exam Room Utilization', itr, 0)

    def update_num_patients(self, time, increment):
        """
        updates the number of patients in the system
        :param time: time of this chance in the system
        :param increment: (integer) change (+ or -) in the number of patients in the system
        """
        self.nOfPatients.record(time, increment)

    def update_utilization(self, time, increment):
        """
        updates the utilization of exam rooms
        :param time: time of this chance in the system
        :param increment: change (+ or -) in the utilization of exam rooms
        """
        self.utilization.record(time, increment)

    def get_sample_paths(self):
        """ :returns samples paths stored during this simulation replicate """

        return [self.nOfPatients, self.utilization]


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, urgent_care):
        """
        :param urgent_care: the urgent care being simulated
        """

        self.urgentCare = urgent_care
        self.nExamRooms = len(urgent_care.examRooms)

        # performance statistics collectors
        self.nPatientsArrived = 0
        self.nPatientServed = 0
        self.patientsInSystem = Stat.ContinuousTimeStat('Number of patients in the urgent care', 0)
        self.patientTimeInSystem = Stat.DiscreteTimeStat('Patient time in the urgent care')
        self.patientWaitingTime = Stat.DiscreteTimeStat('Patient time in waiting room')
        self.examRoomsUtil = Stat.ContinuousTimeStat('Exam room utilization', 0)

        # sample paths
        self.samplePaths = SamplePaths(urgent_care.id)

    def process_patient_arrival(self, patient, time):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        :param time: the arrival time
        """
        self.nPatientsArrived += 1
        self.patientsInSystem.record(time, +1)
        # store the patient arrival time
        patient.tArrived = time

        # update the sample path
        self.samplePaths.update_num_patients(time, +1)

    def process_patient_departure(self, patient, time):
        """ collects statistics for a departing a patient
        :param patient: the patient who is departing
        :param time: the departure time
        """
        self.nPatientServed += 1
        self.patientsInSystem.record(time, -1)
        self.patientTimeInSystem.record(time - patient.tArrived)
        self.patientWaitingTime.record(patient.tLeftWaitingRoom - patient.tJoinedWaitingRoom)
        self.examRoomsUtil.record(time, -1 / self.nExamRooms)

        # update the sample path
        self.samplePaths.update_num_patients(time, -1)
        self.samplePaths.update_utilization(time, -1 / self.nExamRooms)

    def process_start_exam(self, patient, time):
        """ collects statistics for a patient who just started the exam
        :param patient: the patient
        :param time: the time when the patient starts the exam
        """
        self.examRoomsUtil.record(time, +1 / self.nExamRooms)
        self.samplePaths.update_utilization(time, +1 / self.nExamRooms)

    def collect_end_of_sim_stat(self):
        """ collects the performance statistics at the end of this replication of the urgent care simulation """

        # get current simulation time
        t = self.urgentCare.simCal.get_current_time()

        # update sample paths
        self.samplePaths.update_num_patients(t, 0)
        self.samplePaths.update_utilization(t, 0)

        # update performance statistics
        self.patientsInSystem.record(t, 0)
        self.examRoomsUtil.record(t, 0)
        self.urgentCare.waitingRoom.numPatientsWaiting.record(t, 0)

    def print_outputs(self):
        """ prints the collected statistics into a csv file """

        summary = [
            ['Output', 'Mean', 'Confidence Interval', 'Prediction Interval', 'St. Dev.', 'Minimum', 'Maximum'],
            ['Number of patients arrived', self.nPatientsArrived],
            ['Number of patients served', self.nPatientServed],
            self.patientsInSystem.get_summary(D.ALPHA, D.DECI),
            self.urgentCare.waitingRoom.numPatientsWaiting.get_summary(D.ALPHA, D.DECI),
            self.patientTimeInSystem.get_summary(D.ALPHA, D.DECI),
            self.patientWaitingTime.get_summary(D.ALPHA, D.DECI),
            self.examRoomsUtil.get_summary(D.ALPHA, D.DECI)
        ]

        OutSupport.write_csv('Summary-Steady State.csv', summary)


class ColOfUrgentCares:
    """collection of urgent care model """

    def __init__(self, ids):
        """
        :param ids: (list) ids of urgent care models
        """

        self.ids = ids
        self.urgentCares = []   # list of urgent care models

        self.obs_nPatientsArrived = []          # number of patients arrived
        self.obs_nPatientsServed = []           # number of patients served
        self.obs_avePatientsInSystem = []       # average number of patients in system
        self.obs_avePatientsWaiting = []        # average number of patients waiting
        self.obs_avePatientTimeInSystem = []    # average patient time in system
        self.obs_avePatientWaitingTime = []     # average patient waiting time
        self.obs_aveExamRoomsUtilization = []   # average exam room utilization

        self.nPatientsSamplePaths = []          # list of sample paths for number of patients in urgent care

    def simulate(self):
        """ simulate all urgent cares """

        for i in range(len(self.ids)):

            # create an urgent care
            urgent_care = UrgentCare(idn=self.ids[i])

            # simulate the urgent care
            sim_output = urgent_care.simulate(D.SIM_DURATION)

            # collect statistics
            self.obs_nPatientsArrived.append(sim_output.nPatientsArrived)
            self.obs_nPatientsServed.append(sim_output.nPatientServed)
            self.obs_avePatientsInSystem.append(sim_output.patientsInSystem.get_mean())
            self.obs_avePatientsWaiting.append(sim_output.patientWaitingTime.get_mean())
            self.obs_avePatientTimeInSystem.append(sim_output.patientTimeInSystem.get_mean())
            self.obs_avePatientWaitingTime.append(sim_output.patientWaitingTime.get_mean())
            self.obs_aveExamRoomsUtilization.append(sim_output.examRoomsUtil.get_mean())

            # store the sample path for the number of patients in the syste,
            self.nPatientsSamplePaths.append(sim_output.samplePaths.get_sample_paths()[0])

    def print_outputs(self):
        """ prints the collected statistics into a csv file """

        # summary statistics
        n_patients_arrived = Stat.SummaryStat(
            'Number of patients arrived', self.obs_nPatientsArrived)
        n_patients_served = Stat.SummaryStat(
            'Number of patients served', self.obs_nPatientsServed)
        ave_patients_in_system = Stat.SummaryStat(
            'Average number of patients in system', self.obs_avePatientsInSystem)
        ave_patients_waiting =  Stat.SummaryStat(
            'Average number of patients waiting', self.obs_avePatientsWaiting)
        ave_patient_time_in_system = Stat.SummaryStat(
            'Average patient time in system', self.obs_avePatientTimeInSystem)
        ave_patient_waiting_time = Stat.SummaryStat(
            'Average patient waiting time', self.obs_avePatientWaitingTime)
        ave_exam_rooms_utilization = Stat.SummaryStat(
            'Average exam room utilization', self.obs_aveExamRoomsUtilization)

        summary = [
            ['Output', 'Mean', 'Confidence Interval', 'Prediction Interval', 'St. Dev.', 'Minimum', 'Maximum'],
            n_patients_arrived.get_summary(D.ALPHA, D.DECI),
            n_patients_served.get_summary(D.ALPHA, D.DECI),
            ave_patients_in_system.get_summary(D.ALPHA, D.DECI),
            ave_patients_waiting.get_summary(D.ALPHA, D.DECI),
            ave_patient_time_in_system.get_summary(D.ALPHA, D.DECI),
            ave_patient_waiting_time.get_summary(D.ALPHA, D.DECI),
            ave_exam_rooms_utilization.get_summary(D.ALPHA, D.DECI)
        ]

        OutSupport.write_csv('Summary-Transient State.csv', summary)