/**
 * Fixed Scanner Script
 * Removes aggressive blank screen detection and replaces it with a non-intrusive solution
 */
console.log('✅ Fixed scanner script loaded');

// Wait for DOM content to be loaded before doing anything
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM content loaded');
    
    // Only add global error handler to log errors but not take action
    window.addEventListener('error', function(e) {
        console.error('Error caught:', e.message);
        // Don't take any action that could disrupt the page
    });
    
    // Set up form validation on submit
    var scanForm = document.getElementById('scanForm');
    if (scanForm) {
        console.log('✅ Found scan form, setting up validation');
        
        scanForm.addEventListener('submit', function(e) {
            // Basic validation
            var name = document.getElementById('name');
            var email = document.getElementById('email');
            var company = document.getElementById('company');
            var companyWebsite = document.getElementById('company-website');
            var privacyConsent = document.getElementById('privacy-consent');
            
            if (!name || !email || !company || !companyWebsite) {
                console.log('Form elements not found, allowing default form submission');
                return true;
            }
            
            if (!name.value || !email.value || !company.value || !companyWebsite.value || !privacyConsent.checked) {
                alert('Please fill in all required fields and accept the privacy policy.');
                e.preventDefault();
                return false;
            }
            
            // Show progress indicator if found
            var scanProgress = document.getElementById('scanProgress');
            if (scanProgress) {
                // Hide form
                scanForm.style.display = 'none';
                // Show progress
                scanProgress.style.display = 'block';
                
                // Start progress animation if simulation function exists
                if (typeof simulateScanProgress === 'function') {
                    simulateScanProgress();
                }
            }
            
            // Continue with form submission
            return true;
        });
    } else {
        console.log('⚠️ Scan form not found');
    }
});

// Ensure setup for multi-step form if needed
if (typeof setupFormSteps === 'function') {
    // Wait a bit longer for everything to load
    setTimeout(function() {
        try {
            setupFormSteps();
            console.log('✅ Set up form steps');
        } catch (e) {
            console.error('Error setting up form steps:', e);
        }
    }, 500);
}

// Ensure setup for form submission if needed
if (typeof setupFormSubmission === 'function') {
    // Wait a bit longer for everything to load
    setTimeout(function() {
        try {
            setupFormSubmission();
            console.log('✅ Set up form submission');
        } catch (e) {
            console.error('Error setting up form submission:', e);
        }
    }, 500);
}

// Add a small help button to the page that doesn't interfere with anything
setTimeout(function() {
    try {
        // Only add if body exists and doesn't already have a help button
        if (document.body && !document.getElementById('scanner-help-button')) {
            var helpButton = document.createElement('div');
            helpButton.id = 'scanner-help-button';
            helpButton.style.position = 'fixed';
            helpButton.style.bottom = '10px';
            helpButton.style.right = '10px';
            helpButton.style.zIndex = '9999';
            helpButton.style.padding = '8px 12px';
            helpButton.style.backgroundColor = '#f8f9fa';
            helpButton.style.border = '1px solid #ddd';
            helpButton.style.borderRadius = '4px';
            helpButton.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
            helpButton.style.fontSize = '14px';
            helpButton.style.cursor = 'pointer';
            helpButton.style.opacity = '0.7';
            helpButton.style.transition = 'opacity 0.3s ease';
            helpButton.innerHTML = '🛟 Having issues?';
            
            helpButton.onmouseover = function() {
                this.style.opacity = '1';
            };
            
            helpButton.onmouseout = function() {
                this.style.opacity = '0.7';
            };
            
            helpButton.onclick = function() {
                // Get scanner ID from URL
                var scannerMatch = window.location.pathname.match(/scanner\/(.*?)\/embed/);
                var scannerId = scannerMatch ? scannerMatch[1] : '';
                
                if (scannerId) {
                    // Ask user if they want to try simplified version
                    if (confirm('Would you like to try a simplified version of the scanner?')) {
                        window.location.href = '/scanner/' + scannerId + '/minimal';
                    }
                } else {
                    alert('Please contact support if you continue to experience issues.');
                }
            };
            
            document.body.appendChild(helpButton);
        }
    } catch (e) {
        console.error('Error adding help button:', e);
    }
}, 2000);