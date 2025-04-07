// mobile_label_fix.js
document.addEventListener('DOMContentLoaded', function () {
    function isMobileDevice() {
        return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    }

    const waitForUploader = setInterval(() => {
        const labelEl = window.parent.document.querySelector('label[data-testid="stFileUploaderLabel"]');
        if (labelEl) {
            if (isMobileDevice()) {
                labelEl.innerText = "Tap to select images 📱";
            } else {
                labelEl.innerText = "Drag and drop or browse to upload images 🖥️";
            }
            clearInterval(waitForUploader);
        }
    }, 100);
});
