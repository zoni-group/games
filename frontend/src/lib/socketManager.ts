import { socket } from '$lib/socket';

type EventHandler = (...args: any[]) => void;

interface SocketManager {
  listenersAdded: boolean;
  eventHandlers: { [event: string]: Set<EventHandler> };
  addEventListener: (event: string, handler: EventHandler) => void;
  removeEventListener: (event: string, handler: EventHandler) => void;
}

const socketManager: SocketManager = {
  listenersAdded: false,
  eventHandlers: {},
  addEventListener(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = new Set();
      if (socket) {
        socket.on(event, (...args) => {
          this.eventHandlers[event].forEach((h) => h(...args));
        });
      }
    }
    this.eventHandlers[event].add(handler);
  },
  removeEventListener(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].delete(handler);
      if (this.eventHandlers[event].size === 0) {
        // No handlers left for this event
        if (socket) {
          socket.off(event);
        }
        delete this.eventHandlers[event];
      }
    }
  }
};

export default socketManager;
