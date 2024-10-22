// $lib/socket.ts
import { browser } from '$app/environment';
import { io, type Socket } from 'socket.io-client';

declare global {
  interface Window {
    socket: Socket;
  }
}

let socket: Socket;

if (browser) {
  if (!window.socket) {
    window.socket = io({
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      transports: ['websocket'],
      autoConnect: true,
    });
  }
  socket = window.socket;
} else {
  // We're on the server; socket remains undefined
  socket = null;
}

export { socket };
