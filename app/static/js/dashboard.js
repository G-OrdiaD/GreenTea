document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if admin
    if (document.querySelector('.action-links a[href*="edit"]')) {
        initAssignmentSystem();
    }

    // Automatically adds CSRF token to all AJAX requests
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        }
    });

    // Create and style the assignment button
    function initAssignmentSystem() {
        const assignBtn = document.createElement('button');
        assignBtn.className = 'nav-button';
        assignBtn.id = 'assignGreenhouseBtn';
        assignBtn.innerHTML = '<i class="fas fa-user-plus"></i> Assign Greenhouse';
        document.querySelector('.nav-buttons').prepend(assignBtn);

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'assignmentModal';
        modal.className = 'modal';
        modal.style.display = 'none'; // FIXED: Hidden by default
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <h3 style="margin-bottom: 1.5rem;">Assign Greenhouse</h3>
                <form id="assignmentForm">
                    <div class="form-group">
                        <label for="employeeSelect">Employee:</label>
                        <select id="employeeSelect" class="form-select" required>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="greenhouseSelect">Greenhouse:</label>
                        <select id="greenhouseSelect" class="form-select" required>
                            ${Array.from(document.querySelectorAll('#greenhouseSelect option'))
                                .map(opt => opt.outerHTML)
                                .join('')}
                        </select>
                    </div>
                    <button type="submit" class="assign-button">Confirm Assignment</button>
                </form>
            </div>
        `;
        document.body.appendChild(modal);

        const employeeSelect = document.getElementById('employeeSelect');

        // Fetch and populate employees
        fetch('/admin/users', {
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.users) {
                data.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = user.username;
                    employeeSelect.appendChild(option);
                });
            } else {
                console.error('Error fetching or processing user data:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching users:', error);
        });

        // Modal control functions - UPDATED
        const openModal = () => {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // FIXED: Prevent scrolling
        };

        const closeModal = () => {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // FIXED: Re-enable scrolling
        };

        // Event listeners
        assignBtn.addEventListener('click', openModal);
        document.querySelector('.close-modal').addEventListener('click', closeModal);
        window.addEventListener('click', (e) => e.target === modal && closeModal());

        // Form submission
        document.getElementById('assignmentForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';

            try {
                const response = await fetch('/admin/assign', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({
                        employee_id: document.getElementById('employeeSelect').value,
                        greenhouse_id: document.getElementById('greenhouseSelect').value
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('Assignment successful!', 'success');
                    closeModal();
                } else {
                    throw new Error(data.error || 'Assignment failed');
                }
            } catch (error) {
                showAlert(error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Confirm Assignment';
            }
        });
    }

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
});

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

function fetchActiveIssues() {
    fetch('/issues')
        .then(response => response.json())
        .then(data => {
            if (data && data.issues) {
                displayIssues(data.issues);
            } else {
                console.log("No active issues found or error fetching issues.");
            }
        })
        .catch(error => {
            console.error("Error fetching issues:", error);
        });
}

function displayIssues(issues) {
    const issuesContainer = document.getElementById('issues-container');
    issuesContainer.innerHTML = '';

    if (issues.length === 0) {
        issuesContainer.innerHTML = '<p>No active issues.</p>';
        return;
    }

    const ul = document.createElement('ul');
    issues.forEach(issue => {
        const li = document.createElement('li');
        li.textContent = `[${issue.greenhouse_name}] ${issue.message} (Priority: ${issue.priority}, Status: ${issue.status})`;
        ul.appendChild(li);
    });
    issuesContainer.appendChild(ul);
}

document.addEventListener('DOMContentLoaded', fetchActiveIssues);

function submitFeedback() {
    const message = document.getElementById('feedbackMessage').value;
    if (!message.trim()) {
        alert('Please enter a message');
        return;
    }

    fetch("/feedback", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert("Feedback submitted!");
            document.getElementById('feedbackMessage').value = "";
            const modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
            modal.hide();
        } else {
            alert("Something went wrong. Please try again.");
        }
    });
}