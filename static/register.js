const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture');
const faceImageInput = document.getElementById('face_image');

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        alert('Could not access webcam.');
    });

captureBtn.onclick = function() {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/png');
    faceImageInput.value = dataURL;
    canvas.style.display = 'block';
};

// Submit form
const form = document.getElementById('register-form');
form.onsubmit = function(e) {
    if (!faceImageInput.value) {
        alert('Please capture your face first!');
        e.preventDefault();
    }
}; 