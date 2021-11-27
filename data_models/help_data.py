from data_models.enums import Department, Section


class HelpData:

    def __init__(self, department: Department = None, section: Section = None, location: str = "", details: str = ""):
        self.department = department
        self.section = section
        self.location = location
        self.details = details
