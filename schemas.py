from fastapi import Form, File, UploadFile
from pydantic import BaseModel

class BaseForm(BaseModel):
    filename: str
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        filename: str = Form(...),
        file: UploadFile = File(...)
    ):
        return cls(
            filename=filename,
            file=file
        )