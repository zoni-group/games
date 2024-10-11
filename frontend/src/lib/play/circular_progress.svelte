<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let progress: number;
	export let text: string;
	export let color: string;
	let angle = 360 * progress;

	$: angle = 360 * progress;
	$: console.log(angle);

	// Adapt the logic according to the approach
	let background = `radial-gradient(white 50%, transparent 51%),
    conic-gradient(transparent 0deg ${angle}deg, gainsboro ${angle}deg 360deg),
    conic-gradient(green 0deg, green 90deg, green 180deg, green);`;

	$: background = `radial-gradient(white 50%, transparent 51%),
    conic-gradient(transparent 0deg ${angle}deg, gainsboro ${angle}deg 360deg),
    conic-gradient(${color} 0deg, ${color} 90deg, ${color} 180deg, ${color});`;

	$: cssVarStyles = `--background:${background}`;
</script>

<div id="progress-circle" style={cssVarStyles} class="transition-all lg:text-2xl text-base text-black">
	{text}
</div>

<style>
	#progress-circle {
		background: var(--background);
		border-radius: 50%;
		width: 6vw; /* Reduced from 10vw to 6vw */
    	height: 6vw; /* Reduced from 10vw to 6vw */
    	max-width: 72px; /* Reduced from 120px to 72px */
    	max-height: 72px; /* Reduced from 120px to 72px */
		transition: all 500ms ease-in;
		will-change: transform;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
</style>
