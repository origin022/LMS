import adapter from '@sveltejs/adapter-static'; // غيره من auto إلى static

export default {
	kit: {
		adapter: adapter({
			pages: 'build',  // هذا المجلد الذي ينسخه الدوكر
			assets: 'build',
			fallback: 'index.html', // ضروري جداً للـ SPA
			precompress: false,
			strict: true
		})
	}
};