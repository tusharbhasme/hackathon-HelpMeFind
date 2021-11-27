from enum import Enum


class Department(Enum):
    HR = 'HR'
    Healthcare = 'Healthcare'
    Finance = 'Finance'

    def get_sections(self):
        if self.name == Department.HR.name:
            return [e.name for e in HRSection]
        elif self.name == Department.Healthcare.name:
            return [e.name for e in HealthcareSection]
        elif self.name == Department.Finance.name:
            return [e.name for e in FinanceSection]


class Section(Enum):
    pass


class HealthcareSection(Section):
    Doctor = 1
    Medicine = 2
    Bed = 3
    Oxygen = 4
    Mediclaim = 5


class HRSection(Section):
    Recruitment = 1
    Holidays = 2
    Escalation = 3
    Policy = 4


class FinanceSection(Section):
    Salary = 1
    Tax = 2
    Loan = 3


class Location(Enum):
    Pune = 'Pune'
    Gurgaon = 'Gurgaon'
    Chennai = 'Chennai'
    Bangalore = 'Bangalore'
