/**
 * Blank Screen Detection and Redirect
 * 
 * This script is loaded as early as possible and detects if the scanner 
 * is experiencing blank screen issues, then redirects to the minimal scanner.
 */

(function() {
    console.log('🛡️ Blank screen detection running');
    
    // Store the URL components for redirection
    var scannerMatch = window.location.pathname.match(/scanner\/(.*?)\/embed/);
    var scannerId = scannerMatch ? scannerMatch[1] : '';
    var urlParams = new URLSearchParams(window.location.search);
    var clientId = urlParams.get('client_id') || '';
    
    // Check for immediate blank page - very early detection
    if (!document.body || !document.querySelector('head')) {
        console.log('🚨 Critical: Document structure missing - redirecting immediately');
        redirectToMinimalScanner();
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
            console.log('🚨 No visible content detected - redirecting');
            clearInterval(contentCheckInterval);
            redirectToMinimalScanner();
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
            console.log('🚨 Scan form not found or not visible after timeout - redirecting');
            redirectToMinimalScanner();
        }
    }, 3000);
    
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('🚨 Global error caught:', e.message);
        redirectToMinimalScanner();
    });
    
    // Function to redirect to minimal scanner
    function redirectToMinimalScanner() {
        // Cancel any ongoing operations
        try {
            clearInterval(contentCheckInterval);
        } catch(e) {}
        
        // First try showing fallback UI
        try {
            if (document.body) {
                document.body.innerHTML = `
                    <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
                        <h2 style="color: #02054c;">Scanner is loading...</h2>
                        <p>If you are not redirected automatically, click the button below:</p>
                        <button onclick="window.location.href='/scanner/${scannerId}/minimal'" 
                                style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 10px;">
                            Go to Minimal Scanner
                        </button>
                    </div>
                `;
            }
        } catch(e) {
            console.error('Failed to show fallback UI:', e);
        }
        
        // Redirect to minimal scanner
        try {
            var redirectUrl = '/scanner/' + scannerId + '/minimal';
            if (clientId) {
                redirectUrl += '?client_id=' + clientId;
            }
            
            console.log('🔄 Redirecting to:', redirectUrl);
            window.location.href = redirectUrl;
        } catch(e) {
            console.error('Failed to redirect:', e);
            // Last resort - direct to minimal scanner without params
            window.location.href = '/minimal-scanner';
        }
    }
})();