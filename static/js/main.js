// main.js — students will add JavaScript here as features are built

// Demo modal
const overlay = document.getElementById('demo-modal-overlay');
const iframe  = overlay ? overlay.querySelector('.demo-modal-video') : null;

function openModal() {
    iframe.src = iframe.dataset.src;
    overlay.classList.remove('hidden');
}

function closeModal() {
    overlay.classList.add('hidden');
    iframe.src = '';
}

document.getElementById('open-demo-modal')?.addEventListener('click', openModal);
document.getElementById('close-demo-modal')?.addEventListener('click', closeModal);

overlay?.addEventListener('click', function (e) {
    if (e.target === overlay) closeModal();
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !overlay.classList.contains('hidden')) closeModal();
});
