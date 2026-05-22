document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    const errorEl = document.getElementById('register-error');
    const successEl = document.getElementById('register-success');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    // Clear previous messages
    errorEl.textContent = '';
    successEl.textContent = '';
    
    // Validate passwords match
    if (password !== confirmPassword) {
        errorEl.textContent = ' Passwords do not match!';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        errorEl.textContent = ' Password must be at least 6 characters';
        return;
    }
    
    // Disable button during request
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';
    
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ 
                username, 
                email, 
                password 
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Registration failed
            throw new Error(data.detail || 'Registration failed');
        }
        
        // Registration successful
        successEl.textContent = ' Account created successfully! Redirecting to login...';
        
        // Wait 2 seconds then redirect to login page
        setTimeout(() => {
            window.location.href = '/chat.html';
        }, 2000);
        
    } catch (error) {
        errorEl.textContent = `${error.message}`;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
    }
});