document.addEventListener('DOMContentLoaded', async () => {
  let showPWA = await localStorage.getItem('showPWA') || true;

  if (showPWA === true) {
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
    pwaModal.style.top = '6em';
    setTimeout( () => pwaModal.style.top = '-20em', 5000) 

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      addBtn.addEventListener('click', (e) => {
      pwaModal.style.top = '-20em';
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
    });

    window.addEventListener('online', function(e) {
      console.log("You are online");
    }, false);

    document.querySelector('#pwa.modal > svg').addEventListener('click', ev => {
      pwaModal.style.top = '-20em';
    })

    document.querySelector('#never-again').addEventListener('click', ev => {
      pwaModal.style.top = '-20em';
    localStorage.setItem('showPWA', false);
    })
  }

  let root = document.querySelector(':root');
  let userTheme = localStorage.getItem('userTheme') || null;

  if (userTheme != null) {
    if (userTheme === 'dark') {
      root.style.setProperty('--bg-color', '#2c2c2c')
      root.style.setProperty('--font-color', '#cdcdcd')
      root.style.setProperty('--card-bg', '#cdcdcd')
      root.style.setProperty('--link', 'blue')
      root.style.setProperty('--visited-link', 'purple')
    } else if (userTheme === 'light') {
      root.style.setProperty('--bg-color', '#cdcdcd')
      root.style.setProperty('--font-color', '#333')
      root.style.setProperty('--card-bg', '#2c2c2c')
      root.style.setProperty('--link', 'skyblue')
      root.style.setProperty('--visited-link', '#aa7799')
    }
  }

})