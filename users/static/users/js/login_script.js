function toggloPasswordVisibility(el) {
    let password = document.getElementById("id_password");

    if (el.checked) {
        password.type = "text";
    } else {
        password.type = "password";
    }
}