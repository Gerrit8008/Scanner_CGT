/**
 * Quick Scanner Fix
 * This minimal script provides a very simple but direct fix for any blank screen issues
 */

console.log('⚡ Quick scanner fix loaded');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded in quick fix');
    
    // Check if form exists
    const scanForm = document.getElementById('scanForm');
    if (scanForm) {
        console.log('Scan form found - applying quick fix');
        
        // Make sure form submission works even if other scripts fail
        scanForm.addEventListener('submit', function(e) {
            // Let the form submit normally - no AJAX
            console.log('Form submitted via quick fix');
            return true;
        });
    }
    
    // Check for blank body
    setTimeout(function() {
        if (document.body && document.body.innerHTML.trim() === '') {
            console.log('Empty body detected! Fixing...');
            document.body.innerHTML = `
                <div style="padding: 20px; max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;">
                    <h1>Scanner Recovery</h1>
                    <p>The scanner encountered an issue while loading. Please try again.</p>
                    <button onclick="window.location.reload()">Refresh Scanner</button>
                    <a href="/client/scanners">Return to Scanner List</a>
                </div>
            `;
        }
    }, 1000);
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Quick fix caught error:', e.message);
});