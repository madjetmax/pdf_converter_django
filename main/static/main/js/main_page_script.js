let script_data = document.querySelector("#main-script");

// file uploads
const main_form = document.querySelector("#main_form");
const loaded_file = document.querySelector("#loaded_file");
const dropArea = document.querySelector("#file_label");
const fileInput = document.querySelector("#id_file");
// error box
const error_box = document.querySelector("#error_box");

// ad, layers separator, windows, form buttoms
const ad_wrapper = document.querySelector('#ad_wrapper');
const close_ad_button = document.querySelector("#close_btn");
const close_ad_text = document.querySelector("#close_ad_text");

const register_to_download = document.querySelector("#register_to_download_box");
const layers_separator = document.querySelector("#layers_separator");

const load_file_button = document.querySelector("#file_send_button");
const download_button = document.querySelector("#download_btn");


const allowed_extentions = ["pdf"];
function updateLoadedFileCaption(name) {
    loaded_file.innerText = name;

    // check file extention
    let file_extention = name.split('.').pop();
    if (!allowed_extentions.includes(file_extention)) {
        loaded_file.classList.add("invalid-type");
    } else {
        loaded_file.classList.remove("invalid-type");
    }
    // clear error box
    error_box.innerText = "";
} 

fileInput.addEventListener('change', (event) => {
    // clear files if on converting
    if (on_converting) {
        fileInput.value = "";
    } else {
        let file = event.target.files[0];
        updateLoadedFileCaption(file.name);

        // hide ad box and download button
        hideDownloadButton();
        showLoadButton();

        // for download
        download_access_countdown = max_dowload_countdown;
        can_download_file = false;
        can_close_ad = false;
        download_taks_id = null;
        deleteLoadedFileBlob();
    }
});

// Prevent default drag behaviors
["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => e.preventDefault());
    dropArea.addEventListener(eventName, e => e.stopPropagation());
});

// Highlight drop area when item is dragged over it
["dragenter", "dragover"].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
        dropArea.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
        dropArea.classList.remove("dragover");
    });
});

// Handle dropped files
dropArea.addEventListener("drop", e => {
    const files = e.dataTransfer.files;
    fileInput.files = files; // Set files to input
    updateLoadedFileCaption(files[0].name);
});

// sending data and manage ad
let wait_for_task_done = script_data.dataset.waitForTaskDone;

// check user got on page from back button
window.addEventListener('pageshow', function (event) {
    if (event.persisted || performance.getEntriesByType("navigation")[0].type === 'back_forward') {
        wait_for_task_done = false;
    } else {
        if (wait_for_task_done) {
             // start checking task
            startTaskCheck();

            // show ad and layers separator
            showLayersSeparator();
            showAdWrapper();
        }
    }
});


let task_status_check_interval = 2 * 1000; // miliseconds
let download_taks_id = null;

let can_close_ad = false;
let can_download_file = false;

let on_converting = false;

let loaded_file_blob_data = null;

const max_dowload_countdown = 5;
let download_access_countdown = max_dowload_countdown;

function startTaskCheck() {
    on_converting = true;
    let task_id = script_data.dataset.taskId;
    let task_access_token = script_data.dataset.taskAccessToken;
    
    setTimeout(
        () => checkStatus(task_id, task_access_token), 
        1, 
    );
    console.log("waiting");
    
}
// func to seng get requesto for checking task status and errors
async function checkStatus(task_id, task_access_token) {
    let response = await fetch(`/check-task-status/${task_id}/${task_access_token}`);
    let data = await response.json();

    if (data.status === 'processing') {
        setTimeout(() => checkStatus(task_id, task_access_token), task_status_check_interval);
    } 
    else if (data.status === 'success') {
        download_taks_id = task_id;
        can_close_ad = true;
        can_download_file = true;
        await loadFile(task_id, task_access_token);
        showLayersSeparator();
        showAdWrapper(); 
        showDownloadButton();
        showCloseAdText();
        hiddeProgressTitle();
    }
    else if (data.status == "register_to_download") {
        hideAdWrapper();
        showRegisterToDownload();
        showLayersSeparator();
    }
    else {
        console.error("Task failed:", data.message);
    }
}


// for indexed DB
const db_name = "BlobDB";
const store_name = "blobs";
const loaded_file_key = "loaded_file";

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(db_name, 1);

        request.onupgradeneeded = function (event) {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(store_name)) {
                db.createObjectStore(store_name);
            }
        };

        request.onsuccess = function (event) {
            resolve(event.target.result);
        };

        request.onerror = function (event) {
            reject("Database error: " + event.target.errorCode);
        };
    });
}

async function storeLoadedFileBlob(blobData) {
    const db = await openDatabase();
    const tx = db.transaction(store_name, "readwrite");
    const store = tx.objectStore(store_name);

    const request = store.put(blobData, loaded_file_key);

    request.onerror = (e) => console.error("Error storing blob", e);
}

async function getLoadedFileBlob() {
    const db = await openDatabase();
    const tx = db.transaction(store_name, "readonly");
    const store = tx.objectStore(store_name);

    return new Promise((resolve, reject) => {
        const request = store.get(loaded_file_key);

        request.onsuccess = () => {
            if (request.result) {
                resolve(request.result); // returns Blob
            } else {
                reject("No data found");
            }
        };

        request.onerror = (e) => reject("Error retrieving blob", e);
    });
}

async function deleteLoadedFileBlob() {
    const db = await openDatabase();
    const tx = db.transaction(store_name, "readwrite");
    const store = tx.objectStore(store_name);

    const request = store.delete(loaded_file_key);

    request.onerror = (e) => console.error("Error deleting blob", e);
}

async function loadFile(task_id, task_access_token) {
    let file_response = await fetch(`/download-file/${task_id}/${task_access_token}`);
    on_converting = false;
    if (!file_response.ok) {
        return;
    }   
    // get and save data from response
    storeLoadedFileBlob(await file_response.blob());
}

async function downloadFile() {
    if (download_taks_id != null && can_download_file) {
        getLoadedFileBlob().then(blob => {
            // download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.docx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        });
        
        // clear blob file
        deleteLoadedFileBlob();
        can_download_file = false;  
    }
}

function hiddeProgressTitle() {
    let progress_title = document.getElementById("progress_title");
    progress_title.classList.add("hidden");
}

function showAdWrapper() {
    ad_wrapper.classList.remove("hidden");
    ad_wrapper.style.display = "block";
}
function showDownloadButton() {
    download_button.classList.remove("hidden");
}

function closeAd() {
    if (can_close_ad) {
        hideLayersSeparator();
        hideAdWrapper();
    }
}

function showCloseAdText() {
    close_ad_text.classList.remove("hidden");
}

function hideAdWrapper() {
    ad_wrapper.classList.add("hidden");
    ad_wrapper.addEventListener("transitionend", function handleTransitionEnd() {
        ad_wrapper.style.display = "none";
        // Remove event listener to avoid memory leak
        ad_wrapper.removeEventListener("transitionend", handleTransitionEnd);
    });
}

function showLoadButton() {
    load_file_button.classList.remove("hidden");
}

function hideDownloadButton() {
    download_button.classList.add("hidden");
}

function showRegisterToDownload() {
    register_to_download.classList.remove("hidden");
}

function hideLayersSeparator() {
    layers_separator.classList.add("hidden");
}

function showLayersSeparator() {
    layers_separator.classList.remove("hidden");
}