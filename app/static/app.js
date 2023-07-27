document.addEventListener('DOMContentLoaded', async () => {

  let fontSize = localStorage.getItem('fontSize') || 'medium';
  document.querySelector(':root').style.fontSize = fontSize;


  
  let root = document.querySelector(':root');
  let userTheme = localStorage.getItem('userTheme') 
                ? localStorage.getItem('userTheme') 
                : (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) 
                ? 'dark' 
                : 'light';
  let darkModeToggle = document.querySelector('#dark-mode')

  changeTheme(userTheme)

  darkModeToggle.addEventListener('change', ev => {
    let theme = ev.currentTarget.checked ? 'dark' : 'light';
    changeTheme(theme)
    localStorage.setItem('userTheme', theme)
  })

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    changeTheme(localStorage.getItem('userTheme') == null && event.matches ? "dark" : "light");
  });


  function changeTheme(theme) {
    if (theme === 'dark') {
      root.style.setProperty('--bg-color', '#2c2c2c')
      root.style.setProperty('--font-color', '#cdcdcd')
      root.style.setProperty('--card-bg', '#cdcdcd')
      root.style.setProperty('--link', 'blue')
      root.style.setProperty('--visited-link', 'purple')
      darkModeToggle.checked = true;
    } else if (theme === 'light') {
      root.style.setProperty('--bg-color', '#cdcdcd')
      root.style.setProperty('--font-color', '#333')
      root.style.setProperty('--card-bg', '#fff')
      root.style.setProperty('--link', 'skyblue')
      root.style.setProperty('--visited-link', '#aa7799')
      darkModeToggle.checked = false;
    }
  }



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
    const addBtn = document.querySelector('#pwa-btn');
    const pwaModal = document.querySelector('#pwa.modal')

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;

      pwaModal.style.top = '6em';
      setTimeout( () => pwaModal.style.top = '-20em', 5000) 

      addBtn.addEventListener('click', (e) => {
        console.log(e.currentTarget);
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
})


// sidebar script

document.querySelector('#close.sidebar').addEventListener('click', ev =>{
  ev.preventDefault();
  document.querySelector('#sidebar').style.left = '-100vw';
})

document.addEventListener('touchstart', handleTouchStart, false);        
document.addEventListener('touchmove', handleTouchMove, false);

var xDown = null;                                                        
var yDown = null;

function getTouches(evt) {
return  evt.touches;
}                                                     
                                                                      
function handleTouchStart(evt) {
  const firstTouch = getTouches(evt)[0];                                      
  xDown = firstTouch.clientX;                                      
  yDown = firstTouch.clientY;                                      
};                                                
                                                                      
function handleTouchMove(evt) {
  if ( ! xDown || ! yDown ) {
      return;
  }

  var xUp = evt.touches[0].clientX;                                    
  var yUp = evt.touches[0].clientY;

  var xDiff = xDown - xUp;
  var yDiff = yDown - yUp;
                                                                      
  if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
      if ( xDiff > 0 ) {
          /* right swipe */ 
          document.querySelector('#sidebar').style.left = '-100vw';
      } else {
          /* left swipe */
          document.querySelector('#sidebar').style.left = '0';
      }                       
  } else {
      if ( yDiff > 0 ) {
          /* down swipe */ 
      } else { 
          /* up swipe */
      }                                                                 
  }
  /* reset values */
  xDown = null;
  yDown = null;                                             
};