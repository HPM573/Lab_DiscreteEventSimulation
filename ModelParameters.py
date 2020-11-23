import InputData as D
import SimPy.RandomVariateGenerators as RVGs


class Parameters:
    # class to contain the parameters of the urgent care model
    def __init__(self):
        self.hoursOpen = D.HOURS_OPEN
        self.nExamRooms = D.N_EXAM_ROOMS
        self.arrivalTimeDist = RVGs.Exponential(scale=D.MEAN_ARRIVAL_TIME)
        self.examTimeDist = RVGs.Exponential(scale=D.MEAN_EXAM_DURATION)
