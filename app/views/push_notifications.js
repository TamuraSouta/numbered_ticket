
let swRegistration = null;
navigator.serviceWorker.register('sw.js').then(registration => {
    swRegistration = registration;
    return registration.pushManager.getSubscription();
}).then(subscription => {
    if (!subscription) {
    return swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: "YOUR_PUBLIC_VAPID_KEY_HERE"
    });
    } else {
    return subscription;
    }
}).then(subscription => {
  // このサブスクリプション情報をサーバーに送信して保存します
    etch('/save-subscription/', {
    method: 'POST',
    body: JSON.stringify(subscription),
    headers: {
        'Content-Type': 'application/json'
        }
    });
});
