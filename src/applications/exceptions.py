class DuplicateJDException(Exception):
    def __init__(self, company: str, role: str, timestamp: str):
        super().__init__(f"Already analyzed {role} at {company} on {timestamp}")

class ApplicationNotFoundException(Exception):
    def __init__(self, record_id: str):
        super().__init__(f"Application not found: {record_id}")

class InvalidStatusException(Exception):
    VALID = ["applied", "oa", "interviewing", "offer", "rejected", "ghosted"]
    def __init__(self, status: str):
        super().__init__(f"Invalid status: {status}. Choose from {self.VALID}")