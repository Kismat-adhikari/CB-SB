document.addEventListener('DOMContentLoaded', function() {
    // Password validation
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const submitBtn = document.getElementById('submitBtn');
    const passwordRequirements = document.querySelector('.password-requirements');
    
    const commonPasswords = ['password', '123456', 'qwerty', 'abc123', 'letmein', 'admin'];
    
    const requirements = {
        length: { regex: /.{8,}/, element: document.getElementById('length-check') },
        uppercase: { regex: /[A-Z]/, element: document.getElementById('uppercase-check') },
        lowercase: { regex: /[a-z]/, element: document.getElementById('lowercase-check') },
        number: { regex: /[0-9]/, element: document.getElementById('number-check') },
        special: { regex: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/, element: document.getElementById('special-check') },
        match: { element: document.getElementById('match-check') }
    };

    function showPasswordRequirements() {
        passwordRequirements.classList.add('visible');
    }

    function hidePasswordRequirements() {
        if (!passwordInput.value && !confirmPasswordInput.value) {
            passwordRequirements.classList.remove('visible');
        }
    }

    function validatePassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        let isValid = true;

        // Always show requirements if there's any input
        if (password || confirmPassword) {
            showPasswordRequirements();
        }

        // Check common passwords
        if (commonPasswords.includes(password.toLowerCase())) {
            showError('This password is too common. Please choose a stronger password.');
            isValid = false;
            passwordInput.classList.add('shake');
            setTimeout(() => passwordInput.classList.remove('shake'), 500);
        }

        // Check all requirements
        for (let key in requirements) {
            const requirement = requirements[key];
            let passes = false;

            if (key === 'match') {
                passes = password === confirmPassword && password !== '';
            } else {
                passes = requirement.regex.test(password);
            }

            if (requirement.element) {
                requirement.element.classList.toggle('passed', passes);
            }
            isValid = isValid && passes;
        }

        submitBtn.disabled = !isValid;
        return isValid;
    }

    if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('focus', showPasswordRequirements);
        confirmPasswordInput.addEventListener('focus', showPasswordRequirements);
        passwordInput.addEventListener('blur', hidePasswordRequirements);
        confirmPasswordInput.addEventListener('blur', hidePasswordRequirements);
        passwordInput.addEventListener('input', validatePassword);
        confirmPasswordInput.addEventListener('input', validatePassword);
    }

    // Form submission
    const form = document.getElementById('signupForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validatePassword()) {
                e.preventDefault();
                showPasswordRequirements();
                showError('Please ensure all password requirements are met.');
                const firstInvalidInput = form.querySelector('input:invalid');
                if (firstInvalidInput) {
                    firstInvalidInput.classList.add('shake');
                    setTimeout(() => firstInvalidInput.classList.remove('shake'), 500);
                    firstInvalidInput.focus();
                }
            }
        });
    }

    // Username sync with animation
    const usernameInput = document.querySelector('#username');
    if (usernameInput) {
        usernameInput.addEventListener('input', function(e) {
            syncUsername(e.target.value);
        });
    }

    // Enhanced flash message handling
    function showError(message) {
        const container = document.querySelector('.auth-container');
        const existingFlash = document.querySelector('.flash-message');
        
        if (existingFlash) {
            existingFlash.remove();
        }
        
        const flashMessage = document.createElement('div');
        flashMessage.className = 'flash-message';
        flashMessage.textContent = message;
        
        container.insertBefore(flashMessage, container.firstChild);
        
        setTimeout(() => {
            flashMessage.style.opacity = '0';
            flashMessage.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                flashMessage.remove();
            }, 300);
        }, 3000);
    }

    // Initial check for any existing flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    });
});

// Sync username with display name
function syncUsername(value) {
    const displayNameInput = document.querySelector('#display_name');
    if (displayNameInput) {
        displayNameInput.value = value;
    }
}