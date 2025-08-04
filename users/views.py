from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
# django auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from django.template.loader import render_to_string
# models
from .forms import UserRegisterForm, UserLoginForm
from .models import User
from main.models import PageData
# other
from . import tasks
from .tokens import account_activate_token

def get_page_data(request: HttpRequest) -> PageData | None:
    url_name = request.resolver_match.view_name
    try:
        page_data = PageData.objects.get(url_name=url_name)
        return page_data
    except PageData.DoesNotExist:
        return None

# user auth
def send_email_validation(request: HttpRequest, user: User, form: UserRegisterForm):
    current_site = get_current_site(request)
    # create email message and subject
    mail_subject = _("Account Activation")
    message = render_to_string(
        "users/emails/email_activation.html",
        {
            "user": user,
            "protocol": "https" if request.is_secure() else 'http',
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activate_token.make_token(user)
        }
    )
    from_email = "xxx"
    to_email = form.cleaned_data["email"]

    # send using celery
    tasks.send_email_task.delay(
        mail_subject, message, 
        from_email, [to_email]
    )

@csrf_protect
def register_page(request: HttpRequest):
    user = request.user
    if user.is_authenticated:
        return redirect("main_page")

    page_data = get_page_data(request)

    if request.method == "GET":
        reg_form = UserRegisterForm()

    if request.method == "POST":
        reg_form = UserRegisterForm(request.POST)
        if reg_form.is_valid():
            # todo user creation with email verification
            # # create user and send email verification
            # user: User = reg_form.save(commit=False)
            # user.is_active = False
            # user.save()

            # just save form and login user
            user = reg_form.save()
            login(request, user)

            # todo # sending email for validation
            # todo send_email_validation(request, user, reg_form)

            # set messages
            # todo messages.info(request, _("To activate account check your email!"))

            # todo return redirect("users_register")
            return redirect("main_page")
        
    # create content and return page
    context = {
        "form": reg_form,
        "page_data": page_data
    }
    return render(request, "users/register.html", context)

def activate_email(request: HttpRequest, uidb64, token):
    try:
        # check user
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activate_token.check_token(user, token):
        # make user active
        user.is_active = True
        user.save()
    else:
        # return invalid link page
        return render(request, "users/invalid_account_activate_token.html")

    # redirect on login on success
    return redirect("users_login")

@csrf_protect
def login_page(request: HttpRequest):
    user = request.user
    if user.is_authenticated:
        return redirect("main_page")
    
    page_data = get_page_data(request)
    if request.method == "GET":
        login_form = UserLoginForm(request)

    if request.method == "POST":
        login_form = UserLoginForm(request, request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]

            # check user and login
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # clean converted files count to 0
                request.session["converted_files"] = 0

                # get next url or main_page
                redirect_url = request.GET.get("next", "main_page")
                return redirect(redirect_url)
    context = {
        "form": login_form,
        "page_data": page_data
    }
    return render(request, "users/login.html", context)

@csrf_protect
@login_required()
def logout_page(request: HttpRequest):
    if request.method == "GET":
        logout_form = UserLoginForm(request)

    if request.method == "POST":
        logout(request)
        return redirect("users_login")
    
    context = {
        logout_form: "form",
    }
    return render(request, "users/logout.html", context)


# todo for password reset button in template <a href="{% url 'password_reset' %}" class="btn change-password">Spremeni geslo</a>
# profile and other for user
@login_required
def profile_page(request: HttpRequest):
    page_data = get_page_data(request)
    context = {
        "page_data": page_data
    }
    return render(request, "users/profile.html", context)

def send_password_reset_email(request: HttpRequest, user, to_emails):
    current_site = get_current_site(request)
    # create email message and subject
    mail_subject = _("Password Reset")
    message = render_to_string(
        "users/emails/password_reset.html",
        {
            "user": user,
            "protocol": "https" if request.is_secure() else "http",
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        }
    )
    from_email = "xxx"

    # send using celery
    tasks.send_email_task.delay(
        mail_subject, message, 
        from_email, to_emails
    )

@csrf_protect
def reset_password(request: HttpRequest):
    if request.method == "GET":
        reset_form = PasswordResetForm()
    
    if request.method == "POST":
        reset_form = PasswordResetForm(request.POST)
        if reset_form.is_valid():
            # sending email
            email = reset_form.cleaned_data.get("email")
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            if user:
                send_password_reset_email(request, user, [user.email])
                return redirect("password_reset_done")
    context = {
        "form": reset_form
    }
    return render(request, "users/password_reset/password_reset.html", context)