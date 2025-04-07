// script.js

window.addEventListener('DOMContentLoaded', () => {
    const msgElement = document.getElementById("upload-instruction");
    if (window.innerWidth < 768) {
        msgElement.innerText = "Tap to select images (Mobile Friendly)";
    } else {
        msgElement.innerText = "Drag and drop or click to upload";
    }
});
