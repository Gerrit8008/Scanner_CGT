/**
 * Scanner Debug Script
 * This script helps diagnose scanner page loading issues
 */

console.log('🔍 Scanner Debug Script Loading...');

// Report document ready state
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Content Loaded');
    
    // Check for scan form
    const scanForm = document.getElementById('scanForm');
    console.log('Scan form found:', !!scanForm);
    
    if (scanForm) {
        console.log('Scan form action:', scanForm.action);
        console.log('Scan form method:', scanForm.method);
    }
    
    // Check critical elements
    const criticalElements = [
        'scanForm', 'scanProgress', 'scanComplete', 
        'step1', 'step2', 'step3', 'step4'
    ];
    
    criticalElements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`Element #${id} exists:`, !!element);
    });
    
    // Check for JS function conflicts
    if (window.setupFormSteps) {
        console.log('setupFormSteps is defined');
    } else {
        console.error('❌ setupFormSteps is missing!');
    }
    
    if (window.setupFormSubmission) {
        console.log('setupFormSubmission is defined');
    } else {
        console.error('❌ setupFormSubmission is missing!');
    }
    
    // Add error event listener
    window.addEventListener('error', function(e) {
        console.error('Global error caught:', e.message);
        console.error('Error location:', e.filename, 'line', e.lineno, 'column', e.colno);
        
        // Prevent page from going blank on error
        const body = document.body;
        if (body && !body.innerHTML.trim()) {
            body.innerHTML = `
                <div style="padding: 20px; background: #fff; color: #333; max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;">
                    <h1>Scanner Error Detected</h1>
                    <p>The scanner encountered a JavaScript error. Please try refreshing the page or contact support.</p>
                    <div style="background: #f8f8f8; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin-top: 20px;">
                        <h3>Error Details:</h3>
                        <p>${e.message}</p>
                        <p>Location: ${e.filename} (line ${e.lineno}, column ${e.colno})</p>
                    </div>
                    <div style="margin-top: 20px;">
                        <button onclick="window.location.reload()" style="padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Refresh Page</button>
                        <a href="/client/scanners" style="margin-left: 10px; padding: 8px 15px; background: #6c757d; color: white; border: none; border-radius: 4px; text-decoration: none;">Return to Scanners</a>
                    </div>
                </div>
            `;
        }
    });
    
    // Check for jQuery conflicts (if used)
    if (typeof jQuery !== 'undefined') {
        console.log('jQuery version:', jQuery.fn.jquery);
        console.log('jQuery noConflict mode:', typeof $ === 'undefined');
    } else {
        console.log('jQuery is not loaded');
    }
    
    // Check for Bootstrap
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap is loaded');
    } else {
        console.log('Bootstrap is not loaded');
    }
});

// Add a visible UI indicator for debugging when scripts load
const debugIndicator = document.createElement('div');
debugIndicator.style.position = 'fixed';
debugIndicator.style.bottom = '10px';
debugIndicator.style.right = '10px';
debugIndicator.style.padding = '5px 10px';
debugIndicator.style.background = 'rgba(0,0,0,0.7)';
debugIndicator.style.color = 'white';
debugIndicator.style.borderRadius = '4px';
debugIndicator.style.fontSize = '12px';
debugIndicator.style.zIndex = '9999';
debugIndicator.textContent = 'Scanner Debug Active';

// Append to body when it's available
function appendDebugIndicator() {
    if (document.body) {
        document.body.appendChild(debugIndicator);
    } else {
        setTimeout(appendDebugIndicator, 100);
    }
}
appendDebugIndicator();

console.log('🔍 Scanner Debug Script Loaded');

// Check for multiple script loads or function redefinitions
window._scriptLoadCount = window._scriptLoadCount || {};
window._scriptLoadCount['scanner_debug.js'] = (window._scriptLoadCount['scanner_debug.js'] || 0) + 1;
console.log('Scanner debug script load count:', window._scriptLoadCount['scanner_debug.js']);