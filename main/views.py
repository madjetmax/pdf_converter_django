from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from .forms import FileUploadForm
from .models import (
    Advertisement, 
    PageData, 
    TaskAccessToken, 
    BlogParagraph, 
    MainPageOtherInfo,
    QuestionAnswer
)
# celery tasks
from . import tasks 
from celery.result import AsyncResult
from celery import current_app
# other
import datetime
from uuid import uuid4
import tempfile
import os
from copy import deepcopy

def get_page_data(request: HttpRequest) -> PageData | None:
    url = request.path
    try:
        page_data = PageData.objects.get(url=url)
        return page_data
    except PageData.DoesNotExist:
        return None
    
def get_main_page_data(request: HttpRequest):
    # get page data: title description h1
    page_data = get_page_data(request)

    # get other info
    try:
        other_info = MainPageOtherInfo.objects.first()
    except MainPageOtherInfo.DoesNotExist:
        other_info = None

    data = {
        "page_data": page_data,
        "other_info": other_info
    }

    return data

def check_can_convert_files(request: HttpRequest):
    converted_files_count = request.session.get("files_convertions", 0)

    if converted_files_count >= 1:
        return False
    
    converted_files_count += 1
    request.session["files_convertions"] = converted_files_count
    return True

# todo test ad image link https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKmswbD-uU1A6C_jRIJ8oiBEavijias6o8uQ&s

# for files saving 
def get_new_file_name(request: HttpRequest):
    now = datetime.datetime.now()
    formated_now = now.strftime("%d-%b-%Y_%H-%M-%S")
    name = f"{formated_now}_{str(request.user).replace(' ', '-').replace('.', '-')}_{str(uuid4())[:12]}"
    return name

def save_pdf_file(request: HttpRequest) -> str:
    # get file
    file = request.FILES['file']

    if settings.DELETE_PDF_FILES:
        # save pdf tempotary
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            new_file_path = temp_file.name
    else:
        # save pdf to folder
        # get path
        files_folder_path = "loaded_pdf_files"
        new_file_name = get_new_file_name(request) + ".pdf"
        new_file_path = f"{files_folder_path}/{new_file_name}"

        with open(new_file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
    
    return new_file_path

@csrf_protect
def main_page(request: HttpRequest):
    page_data = get_main_page_data(request)

    if request.method == "GET":
        form = FileUploadForm()

        context = {
            "form": form,
            **page_data
        }
        
        return render(request, 'main/main_page.html', context)
    
    if request.method == 'POST':   
        form = FileUploadForm(request.POST, request.FILES)
        
        # get user and access to comvert files
        user = request.user
        user_logged_in = user.is_authenticated

        if form.is_valid():
            # check user and files convertions count
            if not user_logged_in:
                if not check_can_convert_files(request):
                    context = {
                        "form": form,
                        "file_convertion_error": True,
                        "page_data": page_data
                    }
                    return render(request, 'main/main_page.html', context)
            
            # save pdf file
            new_file_path = save_pdf_file(request)
            
            # start convertor task
            task: AsyncResult = tasks.convert_pdf_to_docx.delay(new_file_path, user_logged_in)
            
            # create tast access token
            task_access_token = TaskAccessToken.objects.create(task_id=task.id)
            # selecting random ad
            rand_ad = Advertisement.objects.order_by("?").first()

            # create context and return page
            context = {
                "form": form,
                "submit_error": True,
                "wait_for_task_done": True,
                "task_id": task.id,
                "task_access_token": task_access_token.access_token,
                "ad_model": rand_ad,
                "page_data": page_data
            }
            return render(request, 'main/main_page.html', context)
        
        else:
            # return form with error
            context = {
                "form": form,
                "submit_error": True,
                "page_data": page_data
            }
            return render(request, 'main/main_page.html', context)
    
def check_task_access(task_id, task_access_token) -> TaskAccessToken | None:
    try:
        task = TaskAccessToken.objects.get(task_id=task_id, access_token=task_access_token)
    except TaskAccessToken.DoesNotExist:
        return None
    return task

def get_task_status(request: HttpRequest, task_id, task_access_token):
    if request.method == "GET":
        # check task access
        task_access_token = check_task_access(task_id, task_access_token)
        if not task_access_token:
            return JsonResponse({"error": "invalid access token"})

        task = AsyncResult(task_id)
        # send if task is not done
        if task.state == 'PENDING':
            return JsonResponse({'status': 'processing'})

        # send if task is done
        elif task.state == 'SUCCESS':
            # check if file is scanned and user need to register
            pdf_path, docx_path, need_to_register, _ = task.result
            if need_to_register:
                # delete temp files
                try:
                    os.remove(docx_path)
                    if settings.DELETE_PDF_FILES:
                        os.remove(pdf_path)
                except:
                    pass
                # delete access token
                task_access_token.delete()
                # return error status
                return JsonResponse({'status': 'register_to_download'})
            
            # returns seccess
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': str(task.info)})

def download_file(request: HttpRequest, task_id, task_access_token):
    if request.method == "GET":
        # check task access
        task_access_token = check_task_access(task_id, task_access_token)
        if not task_access_token:
            return JsonResponse({"error": "invalid access token"})

        task = AsyncResult(task_id)

        if task.state != 'SUCCESS':
            return HttpResponse("File is not ready", status=404)
        
        # send file
        # get pdf and docx path
        pdf_path, docx_path, need_to_register, remove_files_task_id = task.result
        if need_to_register:
            return JsonResponse({"message": "register to download scanned file!"})
        
        # delete task access token
        task_access_token.delete()

        # remove files_delete celry task
        remove_files_task = AsyncResult(remove_files_task_id)
        remove_files_task.revoke(terminate=True)

        # read docx file and set it in response
        with open(docx_path, 'rb') as docx_file:
            file_data = docx_file.read()
            response = HttpResponse(file_data, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            response['Content-Disposition'] = f'attachment; filename=converted.docx'
            response['Content-Length'] = len(file_data)  # calculate length of content

        # delete temp files
        try:
            os.remove(docx_path)
            if settings.DELETE_PDF_FILES:
                os.remove(pdf_path)
        except:
            pass
        
        # return content to download
        return response

# other 
def questions_page(request: HttpRequest):
    page_data = get_page_data(request)

    # getting blog paragraphs
    questions_answers = QuestionAnswer.objects.all().order_by("-id")

    context = {
        "page_data": page_data,
        "questions_answers": questions_answers
    }
    return render(request, "main/questions.html", context)


# * for blog
def blog_page(request: HttpRequest):
    page_data = get_page_data(request)
    
    # getting blog paragraphs
    paragraphs = BlogParagraph.objects.all().order_by("-id")

    context = {
        "page_data": page_data,
        "paragraphs": paragraphs
    }
    return render(request, "main/blog.html", context)

def blog_paragraph(request: HttpRequest, url: str):
    # get paragraph by page data
    url_name = request.path
    paragraph = get_object_or_404(BlogParagraph, page_data__url=url_name)

    context = {
        "paragraph": paragraph,
        "page_data": paragraph.page_data,
    }
    return render(request, "main/blog_paragraph.html", context)