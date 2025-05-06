document.addEventListener('DOMContentLoaded', function() {
    // Automatically adds CSRF token to all AJAX requests
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        }
    });

    // Alert/Notification functions
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.padding = '1rem';
        alert.style.borderRadius = '4px';
        alert.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        alert.style.zIndex = '1000';

        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 30000);
    }

    function showNotification(message, type='success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <p>${message}</p>
            <button class="close-notif">&times;</button>
        `;
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 60000);
        notification.querySelector('.close-notif').addEventListener('click', () => {
            notification.remove();
        });
    }

    // Issues functionality
    function fetchActiveIssues() {
        fetch('/issues')
            .then(response => response.json())
            .then(data => {
                if (data && data.issues) {
                    displayIssues(data.issues);
                }
            })
            .catch(console.error);
    }

    function displayIssues(issues) {
        const issuesContainer = document.getElementById('issues-container');
        issuesContainer.innerHTML = issues.length ?
            issues.map(issue =>
                `<li>[${issue.greenhouse_name}] ${issue.message} (Priority: ${issue.priority}, Status: ${issue.status})</li>`
            ).join('') :
            '<p>No active issues.</p>';
    }

    // Feedback functionality
    function submitFeedback() {
        const message = document.getElementById('feedbackMessage').value.trim();
        if (!message) return alert('Please enter a message');

        fetch("/feedback", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Feedback submitted!");
                document.getElementById('feedbackMessage').value = "";
                bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
            } else {
                alert("Something went wrong. Please try again.");
            }
        });
    }

    // Assignment Modal - SINGLE IMPLEMENTATION
    const modal = document.getElementById('assignmentModal');
    const assignBtn = document.getElementById('assignGreenhouseBtn');

    if (modal && assignBtn) {
        // Copy options from hidden selects to modal selects
        function populateDropdowns() {
            const hiddenEmployeeSelect = document.getElementById('employeeSelect');
            const modalEmployeeSelect = modal.querySelector('#employeeSelect');

            if (hiddenEmployeeSelect && modalEmployeeSelect) {
                modalEmployeeSelect.innerHTML = hiddenEmployeeSelect.innerHTML;
            }

            // Greenhouse select is already populated in template
        }

        // Modal control
        assignBtn.addEventListener('click', function(e) {
            e.preventDefault();
            populateDropdowns();
            modal.style.display = 'block';
        });

        document.querySelector('.close-modal').addEventListener('click', function() {
            modal.style.display = 'none';
        });

        window.addEventListener('click', function(e) {
            if (e.target === modal) modal.style.display = 'none';
        });

        // Form submission
        document.getElementById('assignmentForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;

            fetch('/admin/assign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    employee_id: form.querySelector('#employeeSelect').value,
                    greenhouse_id: form.querySelector('#greenhouseSelect').value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                showNotification('Assignment successful!');
                modal.style.display = 'none';
            })
            .catch(error => {
                showNotification(error.message, 'error');
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    // Initialize
    fetchActiveIssues();
    document.getElementById('feedbackForm')?.addEventListener('submit', submitFeedback);
});