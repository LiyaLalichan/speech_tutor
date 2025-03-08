document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const passwordInput = document.querySelector('.password-input');
    const confirmPasswordInput = document.querySelector('.confirm-password');
    const lengthRequirement = document.getElementById('length-requirement');
    const uppercaseRequirement = document.getElementById('uppercase-requirement');
    const numberRequirement = document.getElementById('number-requirement');
    const passwordMatch = document.getElementById('password-match');
    const phoneInput = document.querySelector('input[type="tel"]');
    
    // Real-time password validation
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        
        // Check length requirement
        if (password.length >= 6) {
            lengthRequirement.classList.add('requirement-met');
        } else {
            lengthRequirement.classList.remove('requirement-met');
        }
        
        // Check uppercase requirement
        if (/[A-Z]/.test(password)) {
            uppercaseRequirement.classList.add('requirement-met');
        } else {
            uppercaseRequirement.classList.remove('requirement-met');
        }
        
        // Check number requirement
        if (/[0-9]/.test(password)) {
            numberRequirement.classList.add('requirement-met');
        } else {
            numberRequirement.classList.remove('requirement-met');
        }
        
        // Check if passwords match when confirm password has a value
        if (confirmPasswordInput.value) {
            checkPasswordsMatch();
        }
    });
    
    // Function to check if passwords match
    function checkPasswordsMatch() {
        if (passwordInput.value === confirmPasswordInput.value) {
            passwordMatch.style.display = 'none';
        } else {
            passwordMatch.style.display = 'block';
        }
    }
    
    // Listen for changes to confirm password
    confirmPasswordInput.addEventListener('input', checkPasswordsMatch);
    
    // Phone validation to ensure only numbers
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Limit to 10 digits
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }
});