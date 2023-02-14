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


class Physician:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal):
        """ create a physician
        :param id: (integer) the physician ID
        :param service_time_dist: distribution of service time
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
        """ starts examining the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the physician is busy

        # find the exam completion time (current time + service time)

        # schedule the end of exam

    def remove_patient(self):
        """ remove the patient that was being served """

        # the physician is idle now

        # remove the patient



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
        # waiting room

        # physicians

    def process_new_patient(self, patient, rng):
        """ receives a new patient
        :param patient: the new patient
        :param rng: random number generator
        """



    def process_end_of_exam(self, physician, rng):
        """ processes the end of exam in the specified exam room
        :param physician: the physician that completed their exam
        :param rng: random number generator
        """



    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # close the urgent care
