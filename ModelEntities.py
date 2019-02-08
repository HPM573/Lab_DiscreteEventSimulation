import SimPy.DiscreteEventSim as SimCls
import SimPy.RandomVariantGenerators as RVGs
import ModelEvents as E
import InputData as D
import ModelParameters as P
import ModelOutputs as O


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
    def __init__(self, sim_cal, sim_out, trace):
        """ create a waiting room
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.patientsWaiting = []   # list of patients in the waiting room
        self.simCal = sim_cal       # simulation calendar
        self.simOut = sim_out       # simulation output
        self.trace = trace          # simulation trace

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.process_patient_join_waiting_room(patient=patient)

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room. Number waiting = ' + str(len(self.patientsWaiting)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.process_patient_leave_waiting_room(patient=self.patientsWaiting[0])

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
        """ starts examining on the patient
        :param patient: a patient
        """

        # the exam room is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.urgentCare.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # find the exam completion time (current time + service time)
        exam_completion_time = self.urgentCare.simCal.time \
                               + self.serviceTimeDist.sample(rng=self.urgentCare.rnd)

        # schedule the end of exam
        self.urgentCare.simCal.add_event(
            E.EndOfExam(time=exam_completion_time, exam_room=self, urgent_care=self.urgentCare)
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
        self.params = P.Parameters()  # parameters of this urgent care

        # set up the urgent care
        self.__setup()

    def __setup(self):
        """ sets up the urgent care entities"""

        # set up the simulation calendar
        self.simCal = SimCls.SimulationCalendar()

        # simulation output
        self.simOutputs = O.SimOutputs(sim_cal=self.simCal)

        # set up trace
        self.trace = SimCls.Trace(sim_calendar=self.simCal, if_should_trace=D.TRACE_ON, deci=D.DECI)

        # create a waiting room
        self.waitingRoom = WaitingRoom(sim_cal=self.simCal, sim_out=self.simOutputs, trace=self.trace)

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
            E.CloseUrgentCare(time=self.params.hoursOpen, urgent_care=self)
        )

        # find the arrival time of the first patient
        arrival_time = self.params.arrivalTimeDist.sample(rng=self.rnd)

        # schedule the arrival of the first patient
        self.simCal.add_event(
            E.Arrival(time=arrival_time, patient=Patient(0), urgent_care=self)
        )

    def simulate(self, sim_duration):
        """ simulate the urgent care
        :param sim_duration: duration of simulation
         """

        # initialize the simulation
        self.__initialize()

        # while there is an event scheduled in the simulation calendar
        while self.simCal.n_events() > 0 and self.simCal.time <= sim_duration:
            self.simCal.get_next_event().process()

        # collect the end of simulation statistics
        self.simOutputs.collect_end_of_sim_stat()

    def process_new_patient(self, patient):
        """ receives a new patient
        :param patient: the new patient
        """

        # trace
        self.trace.add_message(
            'Processing arrival of ' + str(patient) + '.')

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            self.trace.add_message('Urgent care closed. '+str(patient)+' does not get admitted.')
            return

        # add the new patient to the list of patients
        self.patients.append(patient)

        # collect statistics
        self.simOutputs.process_patient_arrival(patient)

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
                self.simOutputs.process_start_exam()

        # if no idle room was found
        if not idle_room_found:
            # add the patient to the waiting room
            self.waitingRoom.add_patient(patient=self.patients[-1])

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=self.rnd)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            E.Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1),  # id of the next patient = this patient's id + 1
                urgent_care=self
            )
        )

    def process_end_of_exam(self, exam_room):
        """ processes the end of exam in the specified exam room
        :param exam_room: the exam room where the service is ended
        """

        # trace
        self.trace.add_message('Processing end of exam in ' + str(exam_room) + '.')

        # get the patient who is about to be discharged
        discharged_patient = exam_room.remove_patient()

        # collect statistics
        self.simOutputs.process_patient_departure(
            patient=discharged_patient)

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # start serving the next patient in line
            exam_room.exam(self.waitingRoom.get_next_patient())
            # collect statistics
            self.simOutputs.process_start_exam()

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # trace
        self.trace.add_message('Processing the closing of the urgent care.')

        # close the urgent care
        self.ifOpen = False

    def print_trace(self):
        """ outputs trace """
        self.trace.print_trace(filename="Replication" + str(self.id) + ".txt", directory='Trace')

