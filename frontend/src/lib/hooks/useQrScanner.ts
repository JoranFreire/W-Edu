'use client';

import { useEffect, useRef, useState } from 'react';
import jsQR from 'jsqr';

type ScannerState = 'starting' | 'scanning' | 'unavailable';

/**
 * Le QR pela camera (traseira, se houver): desenha cada quadro num canvas e decodifica com o jsQR,
 * que funciona em qualquer navegador. Pausado (`active` falso), libera a camera.
 */
export function useQrScanner(active: boolean, onCode: (value: string) => void) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [state, setState] = useState<ScannerState>('starting');
  // Sem `mediaDevices` (navegador antigo ou acesso sem HTTPS) nao ha camera.
  const supported = typeof navigator !== 'undefined' && Boolean(navigator.mediaDevices);
  const onCodeRef = useRef(onCode);
  useEffect(() => {
    onCodeRef.current = onCode;
  }, [onCode]);

  useEffect(() => {
    if (!active || !supported) return;
    let stream: MediaStream | null = null;
    let frame = 0;
    let stopped = false;
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d', { willReadFrequently: true });

    const scan = () => {
      const video = videoRef.current;
      if (stopped || !video || !context) return;
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const image = context.getImageData(0, 0, canvas.width, canvas.height);
        const found = jsQR(image.data, image.width, image.height, { inversionAttempts: 'dontInvert' });
        if (found?.data) {
          onCodeRef.current(found.data);
          return;
        }
      }
      frame = requestAnimationFrame(scan);
    };

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(async (media) => {
        stream = media;
        if (stopped || !videoRef.current) return;
        videoRef.current.srcObject = media;
        await videoRef.current.play();
        setState('scanning');
        frame = requestAnimationFrame(scan);
      })
      .catch(() => setState('unavailable'));

    return () => {
      stopped = true;
      cancelAnimationFrame(frame);
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [active, supported]);

  return { videoRef, state: supported ? state : 'unavailable' };
}
