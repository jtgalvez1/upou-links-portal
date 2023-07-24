if ('serviceWorker' in navigator) {
    navigator.serviceWorker
    .register('/service-worker.js')
    .then(function(registration) {
        console.log('Service Worker Registered');
        return registration;
    })
    .catch(function(err) {
        console.error('Unable to register service worker.', err);
    });
}

let deferredPrompt;
const addBtn = document.querySelector('.add-button');
const pwaModal = document.querySelector('#pwa.modal')
// addBtn.style.display = 'none';
pwaModal.style.display = 'none';

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  // addBtn.style.display = 'block';
  pwaModal.style.display = 'block'
  addBtn.addEventListener('click', (e) => {
    // addBtn.style.display = 'none';
    pwaModal.style.display = 'none';
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {


          console.log('User accepted the A2HS prompt');


        } else {

          console.log('User dismissed the A2HS prompt');

        }
        deferredPrompt = null;
      });
  });
  setTimeout( () => pwaModal.style.display = 'none', 5000) 
});

window.addEventListener('online', function(e) {
    console.log("You are online");
}, false);

document.querySelector('#pwa.modal > svg').addEventListener('click', ev => {
  pwaModal.style.display = 'none';
})