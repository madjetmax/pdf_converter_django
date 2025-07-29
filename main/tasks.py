from celery import shared_task
from celery.result import AsyncResult
from pdf2docx import Converter
import fitz

from django.conf import settings
from .models import TaskAccessToken

import os


def contain_images(filepath: str) -> bool:
    with fitz.open(filepath) as file:
        # check images
        for page in file:
            images = page.get_images()
            if images:  
                return True
        return False  # no images in file

@shared_task(bind=True)
def convert_pdf_to_docx(self, temp_pdf_path, can_convert_scanned_file=False) -> tuple[str | None, str | None, bool]:
    """returns temp_pdf_path (or None) temp_docx_path (or None) need_register_to_convert: bool remove_files_task_id"""
    need_register_to_convert = True
    
    # check if file is scanned (has images)
    if not can_convert_scanned_file:
        if contain_images(temp_pdf_path):
            return None, None, need_register_to_convert
    
    need_register_to_convert = False
    
    # convert to docx
    temp_docx_path = temp_pdf_path.replace(".pdf", ".docx")
    cv = Converter(temp_pdf_path)
    cv.convert(temp_docx_path)
    cv.close()

    # delete temporary files in 30 seconds after done
    remove_files_task: AsyncResult = remove_files_and_access_token.apply_async(args=[temp_pdf_path, temp_docx_path, self.request.id], countdown=30)

    return temp_pdf_path, temp_docx_path, need_register_to_convert, remove_files_task.id

@shared_task
def remove_files_and_access_token(temp_pdf_path, temp_docx_path, task_id):
    # delete access token
    try:
        task_access_token = TaskAccessToken.objects.get(task_id=task_id)
        task_access_token.delete()
    except TaskAccessToken.DoesNotExist:
        pass
    
    # delete files
    try:
        os.remove(temp_docx_path)
        if settings.DELETE_PDF_FILES:
            os.remove(temp_pdf_path)
        return "deleted"
    except:
        return None