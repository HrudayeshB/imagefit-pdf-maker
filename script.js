// Scroll Up and Down Buttons
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
function scrollToBottom() {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

const topBtn = document.createElement("button");
topBtn.innerText = "↑";
topBtn.className = "scroll-btn";
topBtn.id = "scroll-top";
topBtn.onclick = scrollToTop;

const bottomBtn = document.createElement("button");
bottomBtn.innerText = "↓";
bottomBtn.className = "scroll-btn";
bottomBtn.id = "scroll-bottom";
bottomBtn.onclick = scrollToBottom;

document.body.appendChild(topBtn);
document.body.appendChild(bottomBtn);
