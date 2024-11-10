export function initFileUpload(uploadFile) {
    const uploadDropzone = document.getElementById('upload-dropzone');
    const uploadInput = document.getElementById('upload-input');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
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

    function highlight() {
        uploadDropzone.classList.add('highlight');
    }

    function unhighlight() {
        uploadDropzone.classList.remove('highlight');
    }

    // Handle dropped files
    uploadDropzone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        return handleFiles(files);
    }

    // Handle files from input element
    uploadInput.addEventListener('change', handleFiles, false);

    function handleFiles(files) {
        return uploadFile(files[0]);
    }
}

export function initExampleUpload(uploadFile) {
    const uploadExample = document.getElementById('upload-example');
    const imageElements = uploadExample.getElementsByTagName('img');
    for (let imageEl of imageElements) {
        imageEl.onclick = (e) => {
            const url = e.target.currentSrc
            const name = url.split('/').pop()
            const ending = name.split('.').pop()
            const fixed_ending = ending === 'jpg' ? 'jpeg' : ending
            const type = 'image/' + fixed_ending
            fetch(url)
                .then(response => response.blob())
                .then(blob => new File([blob], name, {type}))
                .then(file => uploadFile(file))
            ;
        }
    }
}
