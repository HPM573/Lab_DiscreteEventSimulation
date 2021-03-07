from enum import Enum
from SimPy.DiscreteEventSim import SimulationEvent as Event


class Priority(Enum):
    """ priority for processing the urgent care simulation events
    if they are to occur at the exact same time (low number implies higher priority)"""
    ARRIVAL = 1
    END_OF_EXAM = 0
    CLOSE = 2


class Arrival(Event):
    def __init__(self, time, patient, urgent_care):
        """
        creates the arrival of the next patient event
        :param time: time of next patient's arrival
        :param patient: next patient
        :param urgent_care: the urgent care
        """
        # initialize the master class
        Event.__init__(self, time=time, priority=Priority.ARRIVAL.value)

        self.patient = patient
        self.urgentCare = urgent_care

    def process(self, rng=None):
        """ processes the arrival of a new patient """

        # receive the new patient
        self.urgentCare.process_new_patient(patient=self.patient, rng=rng)


class EndOfExam(Event):
    def __init__(self, time, exam_room, urgent_care):
        """
        create the end of service for an specified exam room
        :param time: time of the service completion
        :param exam_room: the exam room
        :param urgent_care: the urgent care
        """
        # initialize the base class
        Event.__init__(self, time=time, priority=Priority.END_OF_EXAM.value)

        self.examRoom = exam_room
        self.urgentCare = urgent_care

    def process(self, rng=None):
        """ processes the end of service event """

        # process the end of service for this exam room
        self.urgentCare.process_end_of_exam(exam_room=self.examRoom, rng=rng)


class CloseUrgentCare(Event):
    def __init__(self, time, urgent_care):
        """
        create the event to close the urgent care
        :param time: time of closure
        :param urgent_care: the urgent care
        """

        self.urgentCare = urgent_care

        # call the master class initialization
        Event.__init__(self, time=time, priority=Priority.CLOSE.value)

    def process(self, rng=None):
        """ processes the closing event """

        # close the urgent care
        self.urgentCare.process_close_urgent_care()
