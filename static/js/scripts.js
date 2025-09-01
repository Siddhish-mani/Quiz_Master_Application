// General form validation
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    // Password confirmation validation
    const password = document.getElementById('password')
    const confirmPassword = document.getElementById('confirm_password')
    
    if (password && confirmPassword) {
        function validatePassword() {
            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity("Passwords don't match")
            } else {
                confirmPassword.setCustomValidity('')
            }
        }
        
        password.onchange = validatePassword
        confirmPassword.onkeyup = validatePassword
    }
    
    // Quiz timer (handled in attempt_quiz.html template)
})

// AJAX functions for admin
function loadChapters(subjectId) {
    fetch(`/admin/api/chapters/${subjectId}`)
        .then(response => response.json())
        .then(data => {
            const chapterSelect = document.getElementById('chapterSelect')
            chapterSelect.innerHTML = ''
            
            if (data.length === 0) {
                const option = document.createElement('option')
                option.value = ''
                option.textContent = 'No chapters available'
                chapterSelect.appendChild(option)
            } else {
                data.forEach(chapter => {
                    const option = document.createElement('option')
                    option.value = chapter.id
                    option.textContent = chapter.name
                    chapterSelect.appendChild(option)
                })
            }
        })
}

// Initialize any page-specific JS
function initPage() {
    // Check if we're on a page with a subject selector
    const subjectSelect = document.getElementById('subjectSelect')
    if (subjectSelect) {
        subjectSelect.addEventListener('change', function() {
            loadChapters(this.value)
        })
        
        // Load chapters if subject is already selected
        if (subjectSelect.value) {
            loadChapters(subjectSelect.value)
        }
    }
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initPage)