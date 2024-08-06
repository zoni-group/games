const config = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				green: {
					600: '#009444'
				}
			},
			fontSize: {
				'fluid-text-sm': 'clamp(0.875rem, 2vw, 2.5rem)', // Small fluid text
				'fluid-text-md': 'clamp(1rem, 3.5vw, 3.5rem)', // Medium fluid text
				'fluid-text-lg': 'clamp(1.5rem, 4vw, 4.5rem)', // Large fluid text
			},
			typography: (theme) => ({
				DEFAULT: {
					css: {
						textDecoration: 'none',
						textColor: '#00529b',
						'code::before': {
							content: '""',
							'padding-left': '0.25rem'
						},
						'code::after': {
							content: '""',
							'padding-right': '0.25rem'
						},
						code: {
							'padding-top': '0.25rem',
							'padding-bottom': '0.25rem',
							fontWeight: '400',
							color: theme('colors.gray.100'),
							'border-radius': '0.25rem',
							backgroundColor: theme('colors.slate.800')
						}
					}
				}
			})
		}
	},
	plugins: [require('@tailwindcss/typography')]
};

module.exports = config;
