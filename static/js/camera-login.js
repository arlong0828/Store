const cameraForm = document.querySelector('[data-camera-login]');

if (cameraForm) {
  const preview = cameraForm.querySelector('[data-camera-preview]');
  const canvas = cameraForm.querySelector('[data-camera-canvas]');
  const imageInput = cameraForm.querySelector('[data-camera-image]');
  const submitButton = cameraForm.querySelector('[data-camera-submit]');
  const status = cameraForm.querySelector('[data-camera-status]');
  const errorBox = cameraForm.querySelector('[data-camera-error]');
  let stream;
  let submitting = false;

  const showError = (message) => {
    errorBox.textContent = message;
    errorBox.hidden = false;
    status.textContent = '相機尚未就緒';
    submitButton.disabled = true;
  };

  const startCamera = async () => {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      showError('此瀏覽器無法安全存取相機，請使用 HTTPS 並更新瀏覽器。');
      return;
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 960 } },
      });
      preview.srcObject = stream;
      await preview.play();
      status.textContent = '請將臉部對準框線';
      submitButton.disabled = false;
    } catch (error) {
      const denied = error.name === 'NotAllowedError' || error.name === 'SecurityError';
      showError(denied
        ? '相機權限遭拒，請在瀏覽器網址列的網站設定中允許相機後重新整理。'
        : '無法啟動相機，請確認相機未被其他程式占用。');
    }
  };

  cameraForm.addEventListener('submit', (event) => {
    if (submitting) return;
    event.preventDefault();

    if (!preview.videoWidth || !preview.videoHeight) {
      showError('相機畫面尚未就緒，請稍候再試。');
      return;
    }

    submitButton.disabled = true;
    status.textContent = '正在擷取並辨識…';
    canvas.width = preview.videoWidth;
    canvas.height = preview.videoHeight;
    const context = canvas.getContext('2d');
    context.translate(canvas.width, 0);
    context.scale(-1, 1);
    context.drawImage(preview, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) {
        showError('無法擷取鏡頭影像，請重新整理後再試。');
        return;
      }
      const transfer = new DataTransfer();
      transfer.items.add(new File([blob], 'face-capture.jpg', { type: 'image/jpeg' }));
      imageInput.files = transfer.files;
      submitting = true;
      stream?.getTracks().forEach((track) => track.stop());
      cameraForm.requestSubmit();
    }, 'image/jpeg', 0.9);
  });

  window.addEventListener('pagehide', () => {
    stream?.getTracks().forEach((track) => track.stop());
  });

  startCamera();
}
