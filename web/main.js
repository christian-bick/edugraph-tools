import "./style.scss";

const UPLOAD_URL = "/api/classify"

const switchView = (oldEl, newEl) => {
    newEl.style.display = "flex";
    oldEl.style.display = "none";
}

const init = () => {
    const viewInit = document.getElementById('view-init')
    const viewClassification = document.getElementById('view-init')
    setTimeout(() => switchView(viewInit, viewClassification), 1000)
    initFileUpload()

}

const initFileUpload = () => {
    const viewUpload = document.getElementById('view-upload');
    const viewProgress = document.getElementById('view-progress');
    const viewResult = document.getElementById('view-result');

    const uploadDropzone = document.getElementById('upload-dropzone');
    const uploadInput = document.getElementById('upload-input');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();

    }

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, unhighlight,
            false);
    });

    function highlight(e) {
        uploadDropzone.classList.add('highlight');
    }

    function unhighlight(e) {
        uploadDropzone.classList.remove('highlight');
    }

    // Handle dropped files
    uploadDropzone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;

        let files = dt.files;

        handleFiles(files);
    }

    // Handle files from input element
    uploadInput.addEventListener('change', handleFiles, false);

    function handleFiles(files) {
        uploadFile(files[0]);
    }

    function previewFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            viewResult.innerHTML = `<img class="file-preview" src="${e.target.result}" alt="${file.name}"/>`;
            switchView(viewProgress, viewResult)
        }
        reader.readAsDataURL(file);
    }

    function uploadFile(file) {
        let url = UPLOAD_URL;
        let formData = new FormData();
        formData.append('file', file);

        switchView(viewUpload, viewProgress)

        fetch(url, {
            method: 'POST',
            body: formData
        })
            .then(response => {
                previewFile(file)
                console.log(response.json())
            })

            .then(data => {
                console.log('Success:', data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

document.addEventListener("DOMContentLoaded", init);