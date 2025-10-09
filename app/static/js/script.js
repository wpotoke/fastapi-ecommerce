document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript is running!');
    const h1 = document.querySelector('h1');
    if (h1) {
        h1.textContent += " - (Loaded by JS)";
    }
});