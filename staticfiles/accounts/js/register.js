function validateRegister() {
    var form = document.register;
    var name = form.name.value.trim();
    var dob = form.dob.value.trim();
    var email = form.email.value.trim();
    var phone = form.phone.value.trim();
    var username = form.username.value.trim();
    var password = form.password.value;
    var confirmPassword = form.confirm_password.value;

    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    var phonePattern = /^[0-9]{10}$/;
    var passwordPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/;

    var valid = true;

    function showError(input, message) {
        var errorSpan = document.getElementById(input + "-error");
        errorSpan.innerText = message;
        errorSpan.style.color = "red";
        valid = false;
    }

    document.querySelectorAll(".error").forEach(span => span.innerText = "");

    if (name === "") showError("name", "Name cannot be empty");
    if (dob === "") showError("dob", "Please enter your Date of Birth");
    if (!emailPattern.test(email)) showError("email", "Enter a valid email");
    if (!phonePattern.test(phone)) showError("phone", "Enter a valid 10-digit phone number");
    if (username === "") showError("username", "Username cannot be empty");
    if (!passwordPattern.test(password)) showError("password", "Password must have 6+ characters, an uppercase, a number & a special character.");
    if (password !== confirmPassword) showError("confirm_password", "Passwords do not match");

    return valid;
}
