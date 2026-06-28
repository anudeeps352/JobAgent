class ResumeNotFoundException(Exception):
    def __init__(self, resume_id:str):
        self.resume_id = resume_id
        self.message = f"Resume with ID '{resume_id}' not found."
        super().__init__(self.message)

class InvalidFileTypeException(Exception):
    def __init__(self, content_type: str):
        self.content_type = content_type
        super().__init__(f"Invalid file type: {content_type}. Only PDFs allowed.")