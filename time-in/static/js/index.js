const temperatureValue = document.getElementById('temperature-value');
const temperatureContainer = document.getElementById('temperature-container');
const temperatureStatus = document.getElementById('temperature-status');

const temperatureHigh = document.getElementById('temperature-high');
const temperatureWarning = document.getElementById('temperature-warning');
const temperatureNormal = document.getElementById('temperature-normal');

let intervalTimeAndDate;
let intervalSerialIr;
let intervalFaceStatus;

async function getFaceStatus(){
     
    const response = await fetch('/api/face/status');
    const data = await response.json();

    if (data === true){
        location.href = "/pages/face-training"
    }
}


function showTempatureStatus(temperatureResult){
    
    temperatureValue.innerHTML =  `${temperatureResult} <sup style=\"vertical-align: top; font-size: 60%;\">°C</sup>`;
    temperatureStatus.innerHTML = "Great! Your temperature is <strong>normal</strong>.";

    temperatureValue.style.color = 'blue';
    temperatureContainer.style.color = 'blue';

    temperatureHigh.classList.add('hidden'); 
    temperatureWarning.classList.add('hidden'); 
    temperatureNormal.classList.remove('hidden'); 

}

function normalTemperature(){
    temperatureValue.innerHTML = data.split(',')[0] + "<sup style=\"vertical-align: top; font-size: 60%;\">°C</sup>";
    temperatureValue.style.color = 'blue';
    temperatureContainer.style.color = 'blue';
    temperatureStatus.innerHTML = "Great! Your temperature is <strong>normal</strong>.";

    temperatureHigh.classList.add('hidden'); 
    temperatureWarning.classList.add('hidden'); 
    temperatureNormal.classList.remove('hidden'); 

}


async function getSerialIr(){

    const response = await fetch('/api/serial-ir');
    const data = await response.json();

    const irResult = parseInt(data.split(',')[1])
    const temperatureResult = parseInt(data.split(',')[0])

    if (parseInt(irResult)=== 0 && parseFloat(temperatureResult) < 39){
        location.href = "/pages/face-recognition";
    }

    

    if (parseFloat(data.split(',')[0]) >= 36 && parseFloat(data.split(',')[0]) <= 38 ){
        document.getElementById('temperature').style.color = '#FFA000';
        document.getElementById('temp_status_container').style.color = '#FFA000';
        document.getElementById('temp_status').innerHTML = "Caution! Your temperature is <strong>slightly high</strong>.";

        document.getElementById('high').classList.add('hidden'); 
        document.getElementById('warning').classList.remove('hidden');
        document.getElementById('normal').classList.add('hidden'); 
    }

    if (parseFloat(data.split(',')[0]) > 39){
        document.getElementById('temperature').style.color = 'red';
        document.getElementById('temp_status_container').style.color = 'red';
        document.getElementById('temp_status').textContent = "Attention! Your <strong>temperature is high</strong>.";

        document.getElementById('high').classList.remove('hidden'); // Hide high icon
        document.getElementById('warning').classList.add('hidden'); // Hide warning icon
        document.getElementById('normal').classList.add('hidden'); // Show normal icon
    }
    
}

function updateTimeAndDate() {
    var currentDate = new Date();

    var hours = currentDate.getHours();
    var minutes = currentDate.getMinutes();
    var amAndPm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    var timeString = hours + ':' + minutes + ' ' + amAndPm;

    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var month = months[currentDate.getMonth()];
    var day = currentDate.getDate();
    var year = currentDate.getFullYear();
    var dateString = month + ' ' + (day < 10 ? '0' + day : day) + ' ' + year;

    document.getElementById('time').textContent = timeString;
    document.getElementById('date').textContent = dateString;
}

function startInterval() {

    intervalTimeAndDate = setInterval(updateTimeAndDate, 1000);
    intervalSerialIr = setInterval(getSerialIr, 1000);
    // intervalFaceStatus = setInterval(getFaceStatus, 500);

}

function stopInterval(){
    clearInterval(intervalTimeAndDate);
    clearInterval(intervalSerialIr);
    // clearInterval(intervalFaceStatus);
}

updateTimeAndDate();
getSerialIr();

window.onload = function() {
    startInterval();
}

window.onunload = function(){
    stopInterval();
}
