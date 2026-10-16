// Main JavaScript file for Certificate Verification UI interactions
document.addEventListener("DOMContentLoaded", function() {
    console.log("CertiBlock Blockchain Certificate Verification System loaded.");

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });
});
