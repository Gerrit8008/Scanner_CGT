// Scanner functionality
const saveAndPreviewScanner = async () => {
    try {
        // Collect form data
        const formData = {
            companyName: document.getElementById('companyName').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            // Add any other form fields you need to collect
        };

        // Validate form data
        if (!validateFormData(formData)) {
            showError('Please fill in all required fields');
            return;
        }

        // Save scanner data to database
        const response = await saveScanner(formData);
        
        if (response.success) {
            // After successful save, redirect to preview page
            window.location.href = `/scanner/preview/${response.scannerId}`;
        } else {
            showError('Failed to save scanner data');
        }
    } catch (error) {
        console.error('Error in saveAndPreviewScanner:', error);
        showError('An unexpected error occurred');
    }
};

// Validation function
const validateFormData = (formData) => {
    // Check required fields
    if (!formData.companyName || !formData.email || !formData.phone) {
        return false;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
        return false;
    }
    
    // Validate phone format (basic validation)
    const phoneRegex = /^\+?[\d\s-]{10,}$/;
    if (!phoneRegex.test(formData.phone)) {
        return false;
    }
    
    return true;
};

// Save scanner data to backend
const saveScanner = async (formData) => {
    try {
        const response = await fetch('/api/scanner/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        // First check if response is redirecting
        if (response.redirected) {
            window.location.href = response.url;
            return { success: true };
        }
        
        const text = await response.text();
        try {
            // Try to parse as JSON
            return JSON.parse(text);
        } catch (e) {
            console.error('Error parsing JSON response:', e);
            console.error('Raw response:', text);
            
            // Check if it's HTML
            if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                console.warn('Server returned HTML instead of JSON');
                
                // Check if it's a success page
                if (text.includes('success') && response.status === 200) {
                    return { 
                        success: true,
                        message: 'Operation completed successfully'
                    };
                }
                
                // Extract error message if possible
                let errorMessage = 'Invalid server response format';
                const errorMatch = text.match(/<div class="alert alert-danger">([^<]+)<\/div>/) || 
                                   text.match(/Error: ([^<]+)/);
                if (errorMatch && errorMatch[1]) {
                    errorMessage = errorMatch[1].trim();
                }
                
                return { 
                    success: false, 
                    error: errorMessage
                };
            }
            
            // Not HTML or JSON
            return { 
                success: false, 
                error: 'Invalid server response format. Please try again or contact support.' 
            };
        }
    } catch (error) {
        console.error('Error saving scanner:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

// Error display function
const showError = (message) => {
    // Assuming you have an error display element
    const errorElement = document.getElementById('errorDisplay');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        alert(message); // Fallback to alert if no error element exists
    }
};

// Add event listener to the Save & Preview button
document.addEventListener('DOMContentLoaded', () => {
    const saveAndPreviewBtn = document.getElementById('saveAndPreviewBtn');
    if (saveAndPreviewBtn) {
        saveAndPreviewBtn.addEventListener('click', saveAndPreviewScanner);
    }
});
// Show loading state
const setLoading = (isLoading) => {
    const saveAndPreviewBtn = document.getElementById('saveAndPreviewBtn');
    if (saveAndPreviewBtn) {
        saveAndPreviewBtn.disabled = isLoading;
        saveAndPreviewBtn.innerHTML = isLoading ? 
            '<span class="spinner-border spinner-border-sm me-2"></span>Saving...' :
            '<i class="bi bi-eye me-2"></i>Save & Preview Scanner';
    }
};

// Show success message
const showSuccess = (message) => {
    const successElement = document.getElementById('successDisplay');
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
        // Hide after 3 seconds
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 3000);
    }
};

// Update the saveAndPreviewScanner function
const saveAndPreviewScanner = async () => {
    try {
        setLoading(true);
        hideError();
        
        const formData = {
            companyName: document.getElementById('companyName').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
        };

        if (!validateFormData(formData)) {
            setLoading(false);
            return;
        }

        const response = await saveScanner(formData);
        
        if (response.success) {
            showSuccess('Scanner saved successfully!');
            // Wait a moment to show the success message
            setTimeout(() => {
                window.location.href = `/scanner/preview/${response.scannerId}`;
            }, 1000);
        } else {
            showError(response.error || 'Failed to save scanner');
        }
    } catch (error) {
        console.error('Error in saveAndPreviewScanner:', error);
        showError('An unexpected error occurred');
    } finally {
        setLoading(false);
    }
};

// Hide error message
const hideError = () => {
    const errorElement = document.getElementById('errorDisplay');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
};
