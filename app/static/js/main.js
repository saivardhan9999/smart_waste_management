// Main JavaScript for Smart Waste Management System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

