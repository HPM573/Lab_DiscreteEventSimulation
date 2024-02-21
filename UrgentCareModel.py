import numpy as np
from deampy.discrete_event_sim import SimulationCalendar

from ModelEntities import UrgentCare, Patient
from ModelEvents import CloseUrgentCare, Arrival


class UrgentCareModel:
    def __init__(self, id, parameters):
        """
        :param id: ID of this urgent care model
        :param parameters: parameters of this model
        """

        self.id = id
        self.params = parameters    # model parameters
        self.simCal = None          # simulation calendar
        self.urgentCare = None      # urgent care

    def simulate(self, sim_duration):
        """ simulate the urgent care
        :param sim_duration: duration of simulation (hours)
         """

        # random number generator
        rng = np.random.RandomState(seed=self.id)

        # initialize the simulation
        self.__initialize(rng=rng)

        # while there is an event scheduled in the simulation calendar
        # and the simulation time is less than the simulation duration
        while self.simCal.n_events() > 0 and self.simCal.time <= sim_duration:
            self.simCal.get_next_event().process(rng=rng)

    def __initialize(self, rng):
        """ initialize the simulation model
        :param rng: random number generator
        """

        # simulation calendar

        # urgent care

        # schedule the closing event

        # find the arrival time of the first patient

        # schedule the arrival of the first patient
