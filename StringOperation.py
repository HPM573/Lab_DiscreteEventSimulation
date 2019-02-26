
class Patient:
    def __init__(self, id, age):
        self.id = id
        self.age = age

    def __str__(self):
        return 'Patient {0} (age {1})'.format(self.id, self.age)


myPatient = Patient(id=1, age=40)

print(str(myPatient), 'arrived.')
