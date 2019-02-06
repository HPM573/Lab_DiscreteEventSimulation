import SimPy.DiscreteEventSim as SimCls
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
        self.patientsWaiting = []
        self.simCal = sim_cal
        self.trace = trace
        # sample path for the patients waiting
        self.numPatientsWaiting = Path.PrevalencePathRealTimeUpdate(
            name='Number of patients waiting', initial_size=0)

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """
        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.get_current_time()
        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)
        # update the sample path
        self.numPatientsWaiting.record(time=self.simCal.get_current_time(), increment=1)
        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room. Number waiting = ' + str(len(self.patientsWaiting)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """
        # update the time the patient leaves the waiting room
        self.patientsWaiting[0].tLeftWaitingRoom = self.simCal.get_current_time()

        # update the sample path of patients waiting
        self.numPatientsWaiting.record(time=self.simCal.get_current_time(), increment=-1)

        # trace
        self.trace.add_message(
            str(self.patientsWaiting[0]) + ' leaves the waiting room. Number waiting = '
            + str(len(self.patientsWaiting) - 1) + '.')

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)


class ExamRoom:
    def __init__(self, id, urgent_care, service_time_dist):
        """ create an exam room
        :param id: (integer) the exam room ID
        :param urgent_care: the urgent care object
        :param service_time_dist: distribution of service time in this exam room
        """
        self.id = id
        self.urgentCare = urgent_care
        self.serviceTimeDist = service_time_dist
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served

    def __str__(self):
        """ :returns (string) the exam room number """
        return "Exam Room " + str(self.id)

    def exam(self, patient):
        """ starts examining on the passed patient
        :param patient: a patient
        """
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.urgentCare.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # find the exam completion time (current time + service time)
        exam_completion_time = self.urgentCare.simCal.get_current_time() \
                               + self.serviceTimeDist.sample(rnd=self.urgentCare.rnd)

        # schedule the end of exam
        self.urgentCare.simCal.add_event(
            Events.EndOfExam(time=exam_completion_time, exam_room=self, urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ :returns the patient that was being served in this exam room"""

        # the exam room is idle now
        self.isBusy = False

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # trace
        self.urgentCare.trace.add_message(str(returned_patient) + ' leaves ' + str(self) + '.')

        return returned_patient


class UrgentCare:
    def __init__(self, id):
        """ creates an urgent care
        :param id: (integer) ID of this urgent care
        :parameter: (Parameters) parameters of this urgent care
        """

        self.id = id                   # urgent care id
        self.ifOpen = True              # if the urgent care is open and admitting new patients
        self.rnd = RVGs.RNG(seed=id)    # random number generator

        # model entities
        self.patients = []          # list of patients
        self.waitingRoom = None     # the waiting room object
        self.examRooms = []         # list of exam rooms
        self.params = Parameters()  # parameters of this urgent care
        self.simOutputs = SimOutputs()  # simulation outputs

        # set up the urgent care
        self.__setup()

    def __setup(self):
        """ sets up the urgent care entities"""

        # set up the simulation calendar
        self.simCal = SimCls.SimulationCalendar()

        # set up trace
        self.trace = SimCls.Trace(sim_calendar=self.simCal, if_should_trace=D.TRACE_ON, deci=D.DECI)

        # create a waiting room
        self.waitingRoom = WaitingRoom(sim_cal=self.simCal, trace=self.trace)

        # create exam rooms
        for i in range(0, self.params.nExamRooms):
            self.examRooms.append(
                ExamRoom(id=i,
                         urgent_care=self,
                         service_time_dist=self.params.examTimeDist)
            )

    def __initialize(self):
        """ initialize simulating the urgent care """

        # schedule the closing event
        self.simCal.add_event(
            Events.CloseUrgentCare(time=self.params.hoursOpen, urgent_care=self)
        )

        # find the arrival time of the first patient
        arrival_time = self.params.arrivalTimeDist.sample(rng=self.rnd)

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
        self.waitingRoom.numPatientsWaiting.record(time=self.simCal.get_current_time(), increment=0)
        self.simOutputs.collect_end_of_sim_stat()

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
        room_index = 0
        while (not idle_room_found) and room_index < len(self.examRooms):
            # if this room is busy
            if self.examRooms[room_index].isBusy:
                # check the next room
                room_index += 1
            else:
                # send the last patient to this exam room
                self.examRooms[room_index].exam(patient=self.patients[-1])
                idle_room_found = True
                # collect statistics
                self.simOutputs.process_start_exam(time=self.simCal.get_current_time())

        # if no idle room was found
        if not idle_room_found:
            # add the patient to the waiting room
            self.waitingRoom.add_patient(patient=self.patients[-1])

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.get_current_time() + self.params.arrivalTimeDist.sample(rng=self.rnd)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            Events.Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.ID + 1),  # id of the next patient = this patient's id + 1
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
        self.simOutputs.process_patient_departure(time=self.simCal.get_current_time())

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # start serving the next patient in line
            exam_room.exam(self.waitingRoom.get_next_patient())
            # collect statistics
            self.simOutputs.process_start_exam(time=self.simCal.get_current_time())

    def print_trace(self):
        """ outputs trace """
        self.trace.print_trace(filename="Replication" + str(self.id) + ".txt", path='../Trace')


class Parameters:
    # class to contain the parameters of the urgent care model
    def __init__(self):
        self.hoursOpen = D.HOURS_OPEN
        self.nExamRooms = D.N_EXAM_ROOMS
        self.arrivalTimeDist = RVGs.Exponential(scale=D.MEAN_ARRIVAL_TIME)
        self.examTimeDist = RVGs.Exponential(scale=D.MEAN_EXAM_DURATION)


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
