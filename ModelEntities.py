from ModelEvents import Arrival, EndOfExam


class Patient:
    def __init__(self, id):
        """ create a patient
        :param id: (integer) patient ID
        """
        self.id = id
        self.tArrived = None               # time the patient arrived
        self.tJoinedWaitingRoom = None     # time the patient joined the waiting room
        self.tLeftWaitingRoom = None       # time the patient left the waiting room


class WaitingRoom:
    def __init__(self, sim_out):
        """ create a waiting room
        :param sim_out: simulation output
        """
        self.patientsWaiting = []   # list of patients in the waiting room
        self.simOut = sim_out

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.collect_patient_joining_waiting_room(patient=patient)

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # update statistics for the patient who leaves the waiting room
        self.simOut.collect_patient_leaving_waiting_room(patient=self.patientsWaiting[0])

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)


class Physician:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out):
        """ create a physician
        :param id: (integer) the physician
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        """
        self.id = id
        self.serviceTimeDist = service_time_dist
        self.urgentCare = urgent_care
        self.simCal = sim_cal
        self.simOut = sim_out
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served

    def __str__(self):
        """ :returns (string) the physician id """
        return "Physician " + str(self.id)

    def exam(self, patient, rng):
        """ starts examining the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the physician is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # collect statistics
        self.simOut.collect_patient_starting_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            EndOfExam(time=exam_completion_time,
                      physician=self,
                      urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ remove the patient that was being served """

        # the physician is idle now
        self.isBusy = False

        # collect statistics
        self.simOut.collect_patient_departure(patient=self.patientBeingServed)

        # remove the patient
        self.patientBeingServed = None


class UrgentCare:
    def __init__(self, id, parameters, sim_cal, sim_out):
        """ creates an urgent care
        :param id: ID of this urgent care
        :param parameters: parameters of this urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        """

        self.id = id
        self.params = parameters
        self.simCal = sim_cal
        self.simOutputs = sim_out

        self.ifOpen = True  # if the urgent care is open and admitting new patients

        # waiting room
        self.waitingRoom = WaitingRoom(sim_out=self.simOutputs)
        # physicians
        self.physicians = []
        for i in range(self.params.nPhysicians):
            self.physicians.append(Physician(id=i,
                                             service_time_dist=self.params.examTimeDist,
                                             urgent_care=self,
                                             sim_cal=self.simCal,
                                             sim_out=self.simOutputs))

    def process_new_patient(self, patient, rng):
        """ receives a new patient
        :param patient: the new patient
        :param rng: random number generator
        """

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            return

        # collect statistics on new patient
        self.simOutputs.collect_patient_arrival(patient=patient)

        # check if anyone is waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # if anyone is waiting, add the patient to the waiting room
            self.waitingRoom.add_patient(patient=patient)
        else:
            # find an idle physician
            idle_physician_found = False
            for physician in self.physicians:
                # if this physician idle
                if not physician.isBusy:
                    # send the last patient to this physician
                    physician.exam(patient=patient, rng=rng)
                    idle_physician_found = True
                    # break the for loop
                    break

            # if no idle physician was found
            if not idle_physician_found:
                # add the patient to the waiting room
                self.waitingRoom.add_patient(patient=patient)

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=rng)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            event=Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1),  # id of the next patient = this patient's id + 1
                urgent_care=self
            )
        )

    def process_end_of_exam(self, physician, rng):
        """ processes the end of exam for this physician
        :param physician: the physician that finished the exam
        :param rng: random number generator
        """

        # remove the patient
        physician.remove_patient()

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:

            # start serving the next patient in line
            physician.exam(patient=self.waitingRoom.get_next_patient(), rng=rng)

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # close the urgent care
        self.ifOpen = False
