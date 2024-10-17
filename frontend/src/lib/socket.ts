// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { io } from 'socket.io-client';

export const socket = io(
    {
        reconnection: true,             // Enable reconnection
        reconnectionAttempts: Infinity, // Retry forever
        reconnectionDelay: 1000,        // Start with a 1-second delay
        reconnectionDelayMax: 5000,     // Maximum delay of 5 seconds
        transports: ['websocket'],      // Use WebSocket transport
        autoConnect: true,              // Automatically connect on creation
    }
);
