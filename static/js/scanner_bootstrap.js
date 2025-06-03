/**
 * Scanner Bootstrap Script - Emergency Recovery
 * This script helps recover from blank screens or JavaScript errors
 */

(function() {
    console.log('🔄 Scanner bootstrap script loaded');
    
    // Check if page is blank (wait a short time to allow normal loading)
    setTimeout(function() {
        // Check if the body is empty
        if (document.body && (!document.body.innerHTML.trim() || document.body.childElementCount <= 1)) {
            console.log('⚠️ Detected potentially blank page, activating emergency recovery');
            
            // Simple recovery UI
            document.body.innerHTML = `
                <div style="padding: 20px; font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
                    <h1 style="color: #02054c;">Scanner Recovery Mode</h1>
                    <p>The scanner encountered a problem while loading. This could be due to a JavaScript error or connectivity issue.</p>
                    
                    <div style="background: #f8f8f8; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h2 style="margin-top: 0; font-size: 18px;">Options:</h2>
                        <button onclick="window.location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Refresh Scanner</button>
                        <a href="/client/scanners" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">Return to Scanner Dashboard</a>
                    </div>
                    
                    <details style="margin-top: 20px;">
                        <summary style="cursor: pointer; padding: 10px; background: #f0f0f0; border-radius: 4px;">Technical Details</summary>
                        <div style="padding: 10px; background: #f8f8f8; margin-top: 5px; border-radius: 4px;">
                            <p>User Agent: ${navigator.userAgent}</p>
                            <p>Page URL: ${window.location.href}</p>
                            <p>Time: ${new Date().toISOString()}</p>
                        </div>
                    </details>
                </div>
            `;
        }
    }, 3000); // Wait 3 seconds before checking
    
    // Add global error recovery
    window.addEventListener('error', function(e) {
        console.error('Bootstrap caught error:', e.message);
        
        // If the error is in a key scanner script and the page is blank
        const isCriticalScript = e.filename && (
            e.filename.includes('scanner.js') || 
            e.filename.includes('fix_scanner_json_parsing.js')
        );
        
        if (isCriticalScript && document.body && (!document.body.innerHTML.trim() || document.body.childElementCount <= 1)) {
            console.log('⚠️ Critical script error detected, activating emergency recovery');
            
            document.body.innerHTML = `
                <div style="padding: 20px; font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
                    <h1 style="color: #dc3545;">Scanner Error Detected</h1>
                    <p>The scanner encountered a JavaScript error. This has been logged for troubleshooting.</p>
                    
                    <div style="background: #f8f8f8; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h3 style="margin-top: 0; color: #dc3545;">Error Details:</h3>
                        <p><strong>Message:</strong> ${e.message}</p>
                        <p><strong>Script:</strong> ${e.filename}</p>
                        <p><strong>Line/Column:</strong> ${e.lineno}:${e.colno}</p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <button onclick="window.location.reload()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Try Again</button>
                        <a href="/client/scanners" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">Return to Scanner Dashboard</a>
                    </div>
                </div>
            `;
        }
    });
})();