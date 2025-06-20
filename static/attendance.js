const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const faceImageInput = document.getElementById('face_image');
const spinner = document.getElementById('spinner');
const form = document.getElementById('attendance-form');

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        // Wait for video to be ready, then auto-capture
        video.onloadedmetadata = () => {
            setTimeout(() => {
                // Show spinner
                spinner.classList.remove('d-none');
                // Capture frame
                canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
                const dataURL = canvas.toDataURL('image/png');
                faceImageInput.value = dataURL;
                // Submit form
                form.submit();
            }, 2000); // 2 seconds delay
        };
    })
    .catch(err => {
        alert('Could not access webcam.');
    }); 