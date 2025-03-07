function startSpeaking() {
    alert("Recording started! Speak now.");
    console.log("Speech recording started...");
}

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("form");
    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();
            alert("Form submitted!");
        });
    }
});
