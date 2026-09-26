// Byte ranges for the landing page's videos.
//
// Cloudflare Pages answers every request for a static file with the whole file, even when
// the browser asks for a byte range. Safari (iPhone, iPad and Mac) will not play a video
// from a server that does that, and other browsers cannot seek into the part that has not
// downloaded yet. This function answers range requests with 206 Partial Content, straight
// from the Pages asset store. The site-dist/_routes.json written by tools/build_site.py
// sends only the .mp4 files here; everything else stays a plain static file.
//
// The asset store hands a file over as a stream with no length, so tools/build_site.py
// writes the sizes into sizes.json at build time.

import sizes from './sizes.json';

export async function onRequest({ request, next }) {
	const range = request.headers.get('Range');
	if (request.method !== 'GET' || !range) return next();
	const match = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
	const asset = await next();
	if (!match || asset.status !== 200 || !asset.body || asset.headers.get('Content-Encoding')) return asset;

	const size = Number(asset.headers.get('Content-Length')) || sizes[new URL(request.url).pathname] || 0;
	if (!size) return asset;
	let start;
	let end;
	if (match[1] === '') {
		// A suffix range: the last n bytes.
		const n = Number(match[2]);
		if (!n) return asset;
		start = Math.max(0, size - n);
		end = size - 1;
	} else {
		start = Number(match[1]);
		end = match[2] === '' ? size - 1 : Math.min(Number(match[2]), size - 1);
	}
	if (start >= size || start > end) {
		await asset.body.cancel();
		return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
	}

	const headers = new Headers(asset.headers);
	headers.delete('Transfer-Encoding');
	headers.set('Accept-Ranges', 'bytes');
	headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
	// The runtime ignores a hand-set Content-Length on a stream; a FixedLengthStream makes
	// it send the exact length, which Safari checks.
	const part = start === 0 && end === size - 1 ? asset.body : slice(asset.body, start, end + 1);
	const { readable, writable } = new FixedLengthStream(end - start + 1);
	part.pipeTo(writable).catch(() => undefined);
	return new Response(readable, { status: 206, headers });
}

/** The bytes [from, to) of a stream, reading no further than needed. */
function slice(body, from, to) {
	const reader = body.getReader();
	let pos = 0;
	return new ReadableStream({
		async pull(controller) {
			for (;;) {
				const { done, value } = await reader.read();
				if (done) {
					controller.close();
					return;
				}
				const chunkStart = pos;
				pos += value.byteLength;
				if (pos <= from) continue;
				const a = Math.max(0, from - chunkStart);
				const b = Math.min(value.byteLength, to - chunkStart);
				if (b > a) controller.enqueue(value.subarray(a, b));
				if (pos >= to) {
					controller.close();
					await reader.cancel();
				}
				return;
			}
		},
		cancel(reason) {
			return reader.cancel(reason);
		},
	});
}
