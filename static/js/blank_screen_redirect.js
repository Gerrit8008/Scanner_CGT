/**
 * Blank Screen Detection and Recovery Option
 * 
 * This script is loaded as early as possible and detects if the scanner 
 * is experiencing blank screen issues, then offers a recovery option
 * instead of automatically redirecting.
 */

(function() {
    console.log('🛡️ Blank screen detection running');
    
    // Store the URL components for redirection
    var scannerMatch = window.location.pathname.match(/scanner\/(.*?)\/embed/);
    var scannerId = scannerMatch ? scannerMatch[1] : '';
    var urlParams = new URLSearchParams(window.location.search);
    var clientId = urlParams.get('client_id') || '';
    
    // Check for immediate blank page - very early detection but only show recovery UI
    if (!document.body || !document.querySelector('head')) {
        console.log('🚨 Critical: Document structure missing - showing recovery option');
        showRecoveryOption();
        return;
    }
    
    // Monitor DOM for content
    var contentCheckInterval = setInterval(function() {
        var hasVisibleContent = false;
        
        // Check if body has visible content
        if (document.body) {
            // Check if there are visible elements
            var visibleElements = document.querySelectorAll('body *');
            for (var i = 0; i < visibleElements.length; i++) {
                var el = visibleElements[i];
                if (el.offsetHeight > 0 && el.innerText && el.innerText.trim()) {
                    hasVisibleContent = true;
                    break;
                }
            }
            
            // Check for form elements specifically
            var formElements = document.querySelectorAll('form, input, button');
            if (formElements.length > 2) {
                hasVisibleContent = true;
            }
        }
        
        if (!hasVisibleContent) {
            console.log('🚨 No visible content detected - showing recovery option');
            clearInterval(contentCheckInterval);
            showRecoveryOption();
        } else {
            console.log('✅ Content detected - scanner appears to be working');
            clearInterval(contentCheckInterval);
        }
    }, 800); // Check faster than the user can perceive
    
    // Final check after reasonable time
    setTimeout(function() {
        clearInterval(contentCheckInterval);
        
        // Check if form is present and visible
        var scanForm = document.getElementById('scanForm');
        var formVisible = scanForm && scanForm.offsetHeight > 0;
        
        if (!formVisible) {
            console.log('🚨 Scan form not found or not visible after timeout - showing recovery option');
            showRecoveryOption();
        }
    }, 3000);
    
    // Global error handler - only show recovery option
    window.addEventListener('error', function(e) {
        console.error('🚨 Global error caught:', e.message);
        showRecoveryOption();
    });
    
    // Function to show recovery option without redirecting
    function showRecoveryOption() {
        // Cancel any ongoing operations
        try {
            clearInterval(contentCheckInterval);
        } catch(e) {}
        
        // Only show recovery UI, don't redirect
        try {
            // Only proceed if we don't already have a recovery option showing
            if (document.getElementById('recovery-option')) {
                return;
            }
            
            if (document.body) {
                var recoveryDiv = document.createElement('div');
                recoveryDiv.id = 'recovery-option';
                recoveryDiv.style.position = 'fixed';
                recoveryDiv.style.top = '50%';
                recoveryDiv.style.left = '50%';
                recoveryDiv.style.transform = 'translate(-50%, -50%)';
                recoveryDiv.style.padding = '20px';
                recoveryDiv.style.background = 'white';
                recoveryDiv.style.border = '1px solid #ddd';
                recoveryDiv.style.borderRadius = '8px';
                recoveryDiv.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
                recoveryDiv.style.zIndex = '9999';
                recoveryDiv.style.maxWidth = '400px';
                recoveryDiv.style.width = '90%';
                recoveryDiv.style.textAlign = 'center';
                
                recoveryDiv.innerHTML = `
                    <h2 style="color: #02054c; margin-top: 0;">Display Issues Detected</h2>
                    <p>The scanner may not be displaying properly. Try one of these options:</p>
                    <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                        <a href="/scanner/${scannerId}/universal" style="display: block; padding: 10px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                            Use Universal Scanner
                        </a>
                        <button onclick="window.location.reload()" style="padding: 10px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            Reload Current Scanner
                        </button>
                        <a href="/client/scanners" style="display: block; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                            Return to Dashboard
                        </a>
                    </div>
                `;
                
                document.body.appendChild(recoveryDiv);
            }
        } catch(e) {
            console.error('Failed to show recovery UI:', e);
        }
    }
})();