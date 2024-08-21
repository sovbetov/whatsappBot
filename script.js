document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    updateProgressBar(50);

    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
            updateProgressBar(0);
        } else {
            console.log('Contacts uploaded:', data);
            localStorage.setItem('contacts', JSON.stringify(data));
            alert('Contacts uploaded successfully!');
            updateProgressBar(100);
        }
    })
    .catch(error => {
        console.error('Error uploading contacts:', error);
        alert(`Error uploading contacts: ${error.message}`);
        updateProgressBar(0);
    });
});

document.getElementById('send-button').addEventListener('click', function() {
    const message = document.getElementById('message-input').value;
    const mediaFile = document.getElementById('media-input').files[0];
    const contacts = JSON.parse(localStorage.getItem('contacts'));

    if (!contacts || contacts.length === 0) {
        alert('No contacts uploaded.');
        return;
    }

    if (mediaFile) {
        const mediaFormData = new FormData();
        mediaFormData.append('file', mediaFile);

        fetch('http://127.0.0.1:5000/upload_media', {
            method: 'POST',
            body: mediaFormData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                console.log('Media uploaded:', data);
                sendMessages(message, contacts, data.filename);
            }
        })
        .catch(error => {
            console.error('Error uploading media:', error);
            alert(`Error uploading media: ${error.message}`);
        });
    } else {
        sendMessages(message, contacts, null);
    }
});

function sendMessages(message, contacts, mediaFilename) {
    updateProgressBar(0);
    const data = {
        contacts: contacts,
        message: message,
        media_path: mediaFilename
    };

    fetch('http://127.0.0.1:5000/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log('Messages sent:', data);
            alert('Messages sent successfully!');
            updateProgressBar(100);
        } else {
            console.error('Error sending messages:', data);
            updateProgressBar(0);
        }
    })
    .catch(error => {
        console.error('Error sending messages:', error);
        alert(`Error sending messages: ${error.message}`);
        updateProgressBar(0);
    });
}

function updateProgressBar(progress) {
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = `${progress}%`;
}
