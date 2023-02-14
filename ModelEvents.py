from deampy.discrete_event_sim import SimulationEvent


""" priority for processing the urgent care simulation events
if they are to occur at the exact same time (low number implies higher priority)"""
ARRIVAL = 1
END_OF_EXAM = 0
CLOSE = 2


class Arrival(SimulationEvent):
    def __init__(self, time, patient, urgent_care):
        """
        creates the arrival of the next patient event
        :param time: time of next patient's arrival
        :param patient: next patient
        :param urgent_care: the urgent care
        """
        # initialize the base class



    def process(self, rng=None):
        """ processes the arrival of a new patient """

        # receive the new patient


class EndOfExam(SimulationEvent):
    def __init__(self, time, physician, urgent_care):
        """
        create the end of service for a specified physician
        :param time: time of the service completion
        :param physician: the physician
        :param urgent_care: the urgent care
        """
        # initialize the base class

    def process(self, rng=None):
        """ processes the end of service event """

        # process the end of service for this physician


class CloseUrgentCare(SimulationEvent):
    def __init__(self, time, urgent_care):
        """
        create the event to close the urgent care
        :param time: time of closure
        :param urgent_care: the urgent care
        """


    def process(self, rng=None):
        """ processes the closing event """

        # close the urgent care
