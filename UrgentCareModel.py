import SimPy.DiscreteEventSim as SimCls
import ModelEvents as E
import ModelEntities as M
import numpy as np


class UrgentCareModel:
    def __init__(self, id, parameters):
        """
        :param id: ID of this urgent care model
        :param parameters: parameters of this model
        """

        self.id = id
        self.params = parameters    # model parameters
        self.rng = None             # random number generator
        self.simCal = None          # simulation calendar
        self.urgentCare = None      # urgent care

    def simulate(self, sim_duration):
        """ simulate the urgent care
        :param sim_duration: duration of simulation (hours)
         """

        # initialize the simulation
        self.__initialize()

        # while there is an event scheduled in the simulation calendar
        # and the simulation time is less than the simulation duration
        while self.simCal.n_events() > 0 and self.simCal.time <= sim_duration:
            self.simCal.get_next_event().process(rng=self.rng)

    def __initialize(self):
        """
        :return: initialize the simulation model
        """

        # random number generator

        # simulation calendar

        # urgent care

        # schedule the closing event

        # find the arrival time of the first patient

        # schedule the arrival of the first patient
