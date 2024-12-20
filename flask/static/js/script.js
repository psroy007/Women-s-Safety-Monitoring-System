document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");
    const verifyOtpForm = document.getElementById("verifyOtpForm");

    // Registration form handling
    if (registerForm) {
        registerForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();

            if (!validateEmail(email)) {
                alert("Please enter a valid email address.");
                return;
            }

            if (!validatePassword(password)) {
                alert("Password must be at least 8 characters long, containing at least one uppercase letter, one lowercase letter, and one number.");
                return;
            }

            // Check if user is already registered
            const storedDetails = JSON.parse(localStorage.getItem("userDetails"));
            if (storedDetails && storedDetails.email === email) {
                alert("This email is already registered. Please log in.");
                return;
            }

            // Save user details in localStorage
            const userDetails = { username, email, password };
            localStorage.setItem("userDetails", JSON.stringify(userDetails));

            alert("Registration successful!");
            window.location.href = "/login"; // Redirect to login page
        });
    }

    // Login form handling
    if (loginForm) {
        loginForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();

            const storedDetails = JSON.parse(localStorage.getItem("userDetails"));
            if (storedDetails && storedDetails.email === email && storedDetails.password === password) {
                alert("Login successful!");
                window.location.href = "/dashboard"; // Redirect to dashboard
            } else {
                alert("Invalid email or password. Please try again.");
            }
        });
    }

    // Forgot Password handling
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            fetch('/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('OTP sent to your email!');
                    document.getElementById('otpVerification').style.display = 'block';
                    forgotPasswordForm.style.display = 'none'; // Hide email form
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(err => {
                console.error('Error sending OTP:', err);
                alert('An error occurred while sending OTP. Please try again.');
            });
        });
    }

    // OTP Verification handling
    if (verifyOtpForm) {
        verifyOtpForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const otp = document.getElementById("otp").value.trim();
            fetch('/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('OTP verified! Please set your new password.');
                    showNewPasswordForm();
                } else {
                    alert('Invalid OTP. Please try again.');
                }
            })
            .catch(err => {
                console.error('Error verifying OTP:', err);
                alert('An error occurred while verifying OTP. Please try again.');
            });
        });
    }

    // Show New Password Form
    function showNewPasswordForm() {
        document.getElementById('otpVerification').innerHTML = `
            <h3>Set New Password</h3>
            <form id="newPasswordForm">
                <label for="newPassword">New Password:</label><br>
                <input type="password" id="newPassword" name="newPassword" required><br><br>
                <label for="confirmPassword">Confirm Password:</label><br>
                <input type="password" id="confirmPassword" name="confirmPassword" required><br><br>
                <button type="submit">Set Password</button>
            </form>
        `;

        document.getElementById("newPasswordForm").addEventListener("submit", (event) => {
            event.preventDefault();

            const newPassword = document.getElementById("newPassword").value.trim();
            const confirmPassword = document.getElementById("confirmPassword").value.trim();

            if (newPassword !== confirmPassword) {
                alert("Passwords do not match. Please try again.");
                return;
            }

            const storedDetails = JSON.parse(localStorage.getItem("userDetails"));
            if (storedDetails && storedDetails.password === newPassword) {
                alert("New password cannot be the same as the old password. Please try again.");
                return;
            }

            // Update password in localStorage
            if (storedDetails) {
                storedDetails.password = newPassword;
                localStorage.setItem("userDetails", JSON.stringify(storedDetails));
            }

            alert("Password updated successfully!");
            window.location.href = "/login"; // Redirect to login page
        });
    }

    // Utility functions
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validatePassword(password) {
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$/;
        return passwordRegex.test(password);
    }
});