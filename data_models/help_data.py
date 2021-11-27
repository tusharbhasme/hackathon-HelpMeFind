from data_models.enums import Department, Location


class HelpData:

    def __init__(self, department: Department = None, section: str = "", location: Location = "", details: str = ""):
        self.department = department
        self.section = section
        self.location = location
        self.details = details
