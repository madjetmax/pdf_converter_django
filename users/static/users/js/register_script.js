function toggloPasswordVisibility(el) {
    let password1 = document.getElementById("id_password1");
    let password2 = document.getElementById("id_password2");

    if (el.checked) {
        password1.type = "text";
        password2.type = "text";
    } else {
        password1.type = "password";
        password2.type = "password";
    }
}