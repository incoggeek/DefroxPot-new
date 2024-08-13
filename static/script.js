// Frame container

 // Function to load content into the iframe
 function loadContent(event, url) {
    event.preventDefault(); // Prevent the default link behavior

    // Get the iframe element
    const iframe = document.getElementById('content-frame');

    // Set the iframe source to the selected URL
    iframe.src = url;
}

// Optional: Load the default content on page load
document.addEventListener('DOMContentLoaded', () => {
    const defaultUrl = "{% url 'website' %}";
    loadContent(null, defaultUrl);
});

// Update

// document.getElementById('update').addEventListener('click', function() {
//     fetch('/update')
//         .then(response => response.json())
//         .then(data => {
//             const status_icon = document.getElementById('update-status');
//             if (data.update_available) {
//                 statusElement.textContent = data.message;
//             } else {
//                 statusElement.textContent = data.message;
//             }
//         })
//         .catch(error => {
//             console.error('Error checking for updates:', error);
//         });
// });

// Action 

document.addEventListener('DOMContentLoaded', function () {
    const button = document.getElementById('server-button');
    const nbutton = document.getElementById('network-button');
    const serverInfo = document.getElementById('server-info');
    const networkInfo = document.getElementById('network-info');
    // let serverStatus = localStorage.getItem('serverStatus');
    // let serverStatus = localStorage.getItem('networkStatus');

    function updateButton(status) {
        if (status === 'running') {
            button.innerHTML = `
                <i class="fa-solid fa-stop"></i>
                <span>Stop</span>
            `;
            button.id = 'server-button';
            button.onclick = stopServer;

        } else if (status === 'stopped') {
            button.innerHTML = `
                <i class="fa-solid fa-play"></i>
                <span>Start</span>
            `;
            button.id = 'server-button';
            button.onclick = startServer;


        } else if (status === 'loading') {
            button.innerHTML = `
                <i class="fa-solid fa-hourglass-start"></i>
                Loading...
            `;
            button.disabled = true;
            button.id = 'server-button';
        }
    }
    function updateButtonnetwork(status) {
        if (status === 'running') {
            nbutton.innerHTML = `
                <i class="fa-solid fa-stop"></i>
                <span>Stop</span>
            `;
            nbutton.id = 'network-button';
            nbutton.onclick = stopNetwork;
        } else if (status === 'stopped') {
            nbutton.innerHTML = `
                <i class="fa-solid fa-play"></i>
                <span>Start</span>
            `;
            nbutton.id = 'network-button';
            nbutton.onclick = startnetwork;
        } else if (status === 'loading') {
            nbutton.innerHTML = `
                <i class="fa-solid fa-hourglass-start"></i>
                Loading...
            `;
            nbutton.disabled = true;
            nbutton.id = 'network-button';
        }
    }

    function startServer() {
        updateButton('loading');
        fetch('/start-flask-server', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    updateButton('running');
                    serverInfo.innerHTML = `Flask server running at ${data.ip}`;
                    // localStorage.setItem('serverStatus', 'running');
                } else {
                    updateButton('stopped');
                }
            });
    }
    function startnetwork() {
        updateButtonnetwork('loading');
        fetch('/start-network-server', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    updateButtonnetwork('running');
                    networkInfo.innerText = "FTP & SSH has started";
                    // localStorage.setItem('serverStatus', 'running');
                } else {
                    updateButtonnetwork('stopped');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function stopServer() {
        updateButton('loading');
        fetch('/stop-flask-server', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'stopped') {
                    updateButton('stopped');
                    serverInfo.innerText = 'Flask Server has stopped';
                    // localStorage.setItem('serverStatus', 'stopped');
                } else {
                    updateButton('running');
                }
            });
    }
    function stopNetwork() {
        updateButtonnetwork('loading');
        fetch('/stop-network-server', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'stopped') {
                    updateButtonnetwork('stopped');
                    networkInfo.innerText = 'FTP & SSH has stopped';
                    // localStorage.setItem('serverStatus', 'stopped');
                } else {
                    updateButtonnetwork('running');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    fetch('/server-setup')
        .then(response => response.json())
        .then(data => {
            updateButton(data.status);
        });
    fetch('/network-setup')
        .then(response => response.json())
        .then(networkStatus => {
            updateButtonnetwork(networkStatus.status);
        });
});


// Copy url

// function copyURL() {
//     const url = window.location.href;  // Get the current URL
//     navigator.clipboard.writeText(url).then(() => {
//         // Show success message
//         const messageElement = document.getElementById('message');
//         messageElement.style.display = 'block';
//         // Hide message after 2 seconds
//         setTimeout(() => {
//             messageElement.style.display = 'none';
//         }, 2000);
//     }).catch(err => {
//         console.error('Failed to copy: ', err);
//     });
// }