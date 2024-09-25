// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { signedIn } from '$lib/stores';

export async function load({ url, parent }) {
	const { email } = await parent();
	if (email) {
		signedIn.set(true);
	}
	const token = url.searchParams.get('pin');
	if (token !== null) {
		return {
			game_pin: token
		};
	}
	// Return an empty object or other data as needed
	return {};
}
