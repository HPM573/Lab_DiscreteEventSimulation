from ModelEvents import Arrival, EndOfExam


class Patient:
    def __init__(self, id):
        """ create a patient
        :param id: (integer) patient ID
        """
        self.id = id


class WaitingRoom:
    def __init__(self):
        """ create a waiting room
        """
        self.patientsWaiting = []   # list of patients in the waiting room

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # add the patient to the list of patients waiting

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # pop the patient

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

        # find the exam completion time (current time + service time)

        # schedule the end of exam

    def remove_patient(self):
        """ :returns the patient that was being served in this exam room"""

        # store the patient to be returned and set the patient that was being served to None

        # the exam room is idle now


class UrgentCare:
    def __init__(self, id, parameters, sim_cal):
        """ creates an urgent care
        :param id: ID of this urgent care
        :param parameters: parameters of this urgent care
        :param sim_cal: simulation calendar
        """

        self.id = id
        self.params = parameters
        self.simCal = sim_cal
        self.nPatientsArrived = 0   # number of patients arrived
        self.nPatientsServed = 0     # number of patients served

        self.ifOpen = True  # if the urgent care is open and admitting new patients

        # model entities
        self.patients = []          # list of patients

        # waiting room

        # exam rooms

    def process_new_patient(self, patient, rng):
        """ receives a new patient
        :param patient: the new patient
        :param rng: random number generator
        """



    def process_end_of_exam(self, exam_room, rng):
        """ processes the end of exam in the specified exam room
        :param exam_room: the exam room where the service is ended
        :param rng: random number generator
        """



    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # close the urgent care
