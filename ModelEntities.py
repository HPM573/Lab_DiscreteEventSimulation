import SimPy.DiscreteEventSim as SimCls
import SimPy.RandomVariantGenerators as RVGs
import ModelEvents as E


class Patient:
    def __init__(self, id):
        """ create a patient
        :param id: (integer) patient ID
        """
        self.id = id


class WaitingRoom:
    def __init__(self, sim_cal):
        """ create a waiting room
        :param sim_cal: simulation calendar
        """
        self.patientsWaiting = []   # list of patients in the waiting room
        self.simCal = sim_cal       # simulation calendar

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)


class ExamRoom:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal):
        """ create an exam room
        :param id: (integer) the exam room ID
        :param service_time_dist: distribution of service time in this exam room
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        """
        self.id = id
        self.serviceTimeDist = service_time_dist
        self.urgentCare = urgent_care
        self.simCal = sim_cal
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served

    def exam(self, patient, rng):
        """ starts examining on the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the exam room is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            E.EndOfExam(time=exam_completion_time, exam_room=self, urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ :returns the patient that was being served in this exam room"""

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # the exam room is idle now
        self.isBusy = False

        return returned_patient


class UrgentCare:
    def __init__(self, id, parameters):
        """ creates an urgent care
        :param id: ID of this urgent care
        :parameters: parameters of this urgent care
        """

        self.id = id                   # urgent care id
        self.rng = RVGs.RNG(seed=id)    # random number generator
        self.ifOpen = True  # if the urgent care is open and admitting new patients

        # model entities
        self.patients = []          # list of patients
        self.waitingRoom = None     # the waiting room object
        self.examRooms = []         # list of exam rooms
        self.params = parameters    # parameters of this urgent care
        self.simCal = SimCls.SimulationCalendar()   # simulation calendar

    def __initialize(self):
        """ initialize simulating the urgent care """

        # create a waiting room
        self.waitingRoom = WaitingRoom(sim_cal=self.simCal)

        # create exam rooms
        for i in range(0, self.params.nExamRooms):
            self.examRooms.append(ExamRoom(id=i,
                                           service_time_dist=self.params.examTimeDist,
                                           urgent_care=self,
                                           sim_cal=self.simCal)
                                  )

        # schedule the closing event
        self.simCal.add_event(
            event=E.CloseUrgentCare(time=self.params.hoursOpen, urgent_care=self))

        # find the arrival time of the first patient
        arrival_time = self.params.arrivalTimeDist.sample(rng=self.rng)

        # schedule the arrival of the first patient
        self.simCal.add_event(
            event=E.Arrival(time=arrival_time, patient=Patient(id=0), urgent_care=self))

    def simulate(self, sim_duration):
        """ simulate the urgent care
        :param sim_duration: duration of simulation
         """

        # initialize the simulation
        self.__initialize()

        # while there is an event scheduled in the simulation calendar
        # and the simulation time is less than the simulation duration
        while self.simCal.n_events() > 0 and self.simCal.time <= sim_duration:
            self.simCal.get_next_event().process()

    def process_new_patient(self, patient):
        """ receives a new patient
        :param patient: the new patient
        """

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            return

        # add the new patient to the list of patients
        self.patients.append(patient)

        # find an idle exam room
        idle_room_found = False
        for room in self.examRooms:
            # if this room is busy
            if not room.isBusy:
                # send the last patient to this exam room
                room.exam(patient=patient, rng=self.rng)
                idle_room_found = True
                # break the for loop
                break

        # if no idle room was found
        if not idle_room_found:
            # add the patient to the waiting room
            self.waitingRoom.add_patient(patient=patient)

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=self.rng)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            event=E.Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1),  # id of the next patient = this patient's id + 1
                urgent_care=self
            )
        )

    def process_end_of_exam(self, exam_room):
        """ processes the end of exam in the specified exam room
        :param exam_room: the exam room where the service is ended
        """

        # get the patient who is about to be discharged
        discharged_patient = exam_room.remove_patient()

        # remove the discharged patient from the list of patients
        self.patients.remove(discharged_patient)

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:

            # start serving the next patient in line
            exam_room.exam(patient=self.waitingRoom.get_next_patient(), rng=self.rng)

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # close the urgent care
        self.ifOpen = False

