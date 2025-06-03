/**
 * Scanner JSON Parsing Fix Script
 * 
 * This script adds robust JSON parsing error handling to the scanner API calls.
 * It patches the global fetch API to better handle HTML responses when JSON is expected.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Scanner JSON parsing fix loaded');
    
    // Create a utility function to safely parse JSON
    window.safeParseJSON = function(text) {
        if (!text) return { success: false, error: 'Empty response' };
        
        try {
            return JSON.parse(text);
        } catch (e) {
            console.error('JSON parse error:', e);
            console.error('Raw text:', text.substring(0, 1000) + (text.length > 1000 ? '...' : ''));
            
            // Check if it's HTML
            if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                console.warn('Server returned HTML instead of JSON');
                
                // Try to extract error message from HTML
                let errorMsg = 'Server returned HTML instead of JSON';
                const errorMatch = text.match(/<div class="alert alert-danger">([^<]+)<\/div>/) || 
                                   text.match(/Error: ([^<]+)/) ||
                                   text.match(/<p class="error">([^<]+)<\/p>/);
                                   
                if (errorMatch && errorMatch[1]) {
                    errorMsg = errorMatch[1].trim();
                }
                
                return { 
                    success: false, 
                    error: errorMsg,
                    isHtml: true,
                    htmlContent: text
                };
            }
            
            return { 
                success: false, 
                error: 'Invalid JSON response: ' + e.message
            };
        }
    };
    
    // Enhance all form submissions to better handle JSON parsing errors
    document.querySelectorAll('form').forEach(form => {
        // Only enhance forms that submit to endpoints that might return JSON
        const formAction = form.getAttribute('action') || '';
        if (formAction.includes('/scan') || 
            formAction.includes('/api') || 
            formAction.includes('/scanner')) {
            
            // Store original onsubmit
            const originalOnSubmit = form.onsubmit;
            
            form.onsubmit = function(e) {
                // If there's an original handler and it returns false, respect that
                if (typeof originalOnSubmit === 'function' && originalOnSubmit(e) === false) {
                    return false;
                }
                
                // Only handle forms without AJAX submission already set up
                if (!form.dataset.ajaxHandled) {
                    e.preventDefault();
                    
                    // Create FormData
                    const formData = new FormData(form);
                    
                    // Set headers
                    const headers = {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json, text/html'
                    };
                    
                    // Submit form
                    fetch(form.action, {
                        method: form.method || 'POST',
                        headers: headers,
                        body: formData
                    })
                    .then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;
                            return null;
                        }
                        
                        // Get content type
                        const contentType = response.headers.get('content-type');
                        
                        if (contentType && contentType.includes('application/json')) {
                            // JSON response
                            return response.text().then(text => {
                                return { 
                                    text, 
                                    isJson: true, 
                                    status: response.status 
                                };
                            });
                        } else {
                            // HTML or other response
                            return response.text().then(text => {
                                return { 
                                    text, 
                                    isJson: false, 
                                    status: response.status 
                                };
                            });
                        }
                    })
                    .then(result => {
                        if (!result) return; // Redirected
                        
                        if (result.isJson) {
                            // Parse JSON safely
                            const data = window.safeParseJSON(result.text);
                            
                            if (data.success) {
                                // Handle success - redirect or show success message
                                if (data.redirect) {
                                    window.location.href = data.redirect;
                                } else if (data.message) {
                                    alert('Success: ' + data.message);
                                    // You might want to reload or redirect
                                }
                            } else {
                                // Show error
                                alert('Error: ' + (data.error || 'Unknown error occurred'));
                            }
                        } else {
                            // HTML response
                            if (result.status >= 400) {
                                // Error page
                                const errorMatch = result.text.match(/<div class="alert alert-danger">([^<]+)<\/div>/) || 
                                                 result.text.match(/Error: ([^<]+)/);
                                if (errorMatch && errorMatch[1]) {
                                    alert('Error: ' + errorMatch[1].trim());
                                } else {
                                    alert('Error: The server returned an error page.');
                                }
                            } else {
                                // Success page - just redirect to it
                                document.open();
                                document.write(result.text);
                                document.close();
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Form submission error:', error);
                        alert('Error: ' + error.message);
                    });
                    
                    return false;
                }
            };
        }
    });
    
    // Fix for JSON parsing in scanner API
    try {
        // If there's a scan form with API submission
        const scanForm = document.getElementById('scanForm');
        const apiScanForm = document.getElementById('apiScanForm');
        
        if (scanForm || apiScanForm) {
            console.log('📝 Enhanced scanner form found, applying JSON parsing fix');
            
            // Add global handler for JSON fetch responses
            const originalFetch = window.fetch;
            window.fetch = function() {
                return originalFetch.apply(this, arguments)
                    .then(response => {
                        // Store the original response.json function
                        const originalJson = response.json;
                        
                        // Override the json function with our safe version
                        response.json = function() {
                            return response.text().then(text => {
                                try {
                                    return JSON.parse(text);
                                } catch (e) {
                                    console.error('JSON parse error in fetch:', e);
                                    console.error('Response text:', text.substring(0, 1000));
                                    
                                    // Check if HTML response
                                    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                                        throw new Error('Server returned HTML instead of JSON. Please check server logs or try again.');
                                    }
                                    
                                    throw new Error('Failed to parse JSON: ' + e.message);
                                }
                            });
                        };
                        
                        return response;
                    });
            };
        }
    } catch (error) {
        console.error('Error setting up scan form enhancements:', error);
    }
});