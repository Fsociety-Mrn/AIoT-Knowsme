const formContainer = document.getElementById('formContainer');
const employeeId = document.getElementById('employeeId');
const errorStatus = document.getElementById('errorStatus');

const facialRegistrationContainer = document.getElementById('facialRegistrationContainer');
const facialVideo = document.getElementById('facialVideo');
const facialCaptureCounter = document.getElementById('facialCaptureCounter');
const captureCount = document.getElementById('captureCount');

let interval;


function showSuccessForm(){
    employeeId.classList.remove('is-invalid');
    employeeId.classList.add('is-valid');
    errorStatus.classList.add('d-none');

    formContainer.classList.add('d-none');
    facialRegistrationContainer.classList.remove('d-none')
    facialVideo.src = src="/api/face-register/detect-face"
}


function showErrorForm(){
    errorStatus.classList.remove('d-none');
    employeeId.classList.add('is-invalid');
}


async function idValidate(event){
    event.preventDefault();

    const response = await fetch('/api/face-register/id-verifications', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'employee_id': employeeId.value 
        })
    });


    if (!response.ok) {
        showErrorForm();
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    showSuccessForm();
    startInterval();

}


async function getCameraStatusAndCounter(){

    const response = await fetch('/api/face-register/capture-counter');
    const data =  await response.json();

    if (data.is_camera_connected == false){
        facialCaptureCounter.classList.remove("d-none");
    }
    facialStatus.innerText = data.camera_message == "" ? "Please hold on! We're starting up your camera..." : data.camera_message;
    captureCount.innerText = data.capture_counter;

}


async function proceedToFacialTraining(){

    const response = await fetch('/api/face-register/status');
    const data =  await response.json();

    if (data === "sending"){
        location.href = "/pages/face-training"
    }

}


function startInterval() {
    interval = setInterval(
        function (){
            getCameraStatusAndCounter();
            proceedToFacialTraining();
    }, 500); 
}


function stopInterval() {
    clearInterval(interval);
}


window.addEventListener('beforeunload', stopInterval());