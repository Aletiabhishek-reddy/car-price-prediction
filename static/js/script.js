/* =========================================================
   CARPREDICT JAVASCRIPT
   ========================================================= */


function togglePassword() {

    const password =
        document.getElementById("password");

    const button =
        document.querySelector(".password-toggle");

    if (!password) {
        return;
    }

    if (password.type === "password") {

        password.type = "text";

        if (button) {
            button.textContent = "🙈";
        }

    } else {

        password.type = "password";

        if (button) {
            button.textContent = "👁";
        }
    }
}


function toggleRegisterPassword(id) {

    const password =
        document.getElementById(id);

    if (!password) {
        return;
    }

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}


/* Automatically remove flash messages */

setTimeout(function () {

    const messages =
        document.querySelectorAll(".flash");

    messages.forEach(function (message) {

        message.style.opacity = "0";

        message.style.transform =
            "translateY(-5px)";

        message.style.transition =
            "all 0.3s ease";

        setTimeout(function () {
            message.remove();
        }, 300);

    });

}, 5000);