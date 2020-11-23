import SimPy.InOutFunctions as IO
import SimPy.RandomVariateGenerators as RVGs
import SimPy.DiscreteEventSim as SimCls
import SimPy.SimulationSupport as Sim
import InputData as D
import ModelOutputs as O
import ModelEvents as E
import ModelEntities as M


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
        self.simOutputs = None      # simulation outputs
        self.trace = None           # simulation trace
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

        # collect the end of simulation statistics
        self.simOutputs.collect_end_of_simulation()

    def __initialize(self):
        """
        :return: initialize the simulation model
        """

        # random number generator
        self.rng = RVGs.RNG(seed=self.id)

        # simulation calendar
        self.simCal = SimCls.SimulationCalendar()

        # simulation outputs
        self.simOutputs = O.SimOutputs(sim_cal=self.simCal,
                                       warm_up_period=D.WARM_UP,
                                       trace_on=D.TRACE_ON)

        # simulation trace
        self.trace = Sim.DiscreteEventSimTrace(sim_calendar=self.simCal,
                                               if_should_trace=D.TRACE_ON,
                                               deci=D.DECI)

        # urgent care
        self.urgentCare = M.UrgentCare(id=id,
                                       parameters=self.params,
                                       sim_cal=self.simCal,
                                       sim_out=self.simOutputs,
                                       trace=self.trace)

        # schedule the closing event
        self.simCal.add_event(
            event=E.CloseUrgentCare(time=self.params.hoursOpen,
                                    urgent_care=self.urgentCare)
        )

        # find the arrival time of the first patient
        arrival_time = self.params.arrivalTimeDist.sample(rng=self.rng)

        # schedule the arrival of the first patient
        self.simCal.add_event(
            event=E.Arrival(time=arrival_time,
                            patient=M.Patient(id=0),
                            urgent_care=self.urgentCare)
        )

    def print_trace(self):
        """ outputs trace """

        # simulation trace
        self.trace.print_trace(filename='Trace-Replication' + str(self.id) + '.txt',
                               directory='Trace',
                               delete_existing_files=True)
        # patient summary
        IO.write_csv(file_name='Patients-Replication' + str(self.id) + '.txt',
                     rows=self.simOutputs.patientSummary,
                     directory='Patients Summary',
                     delete_existing_files=True)
