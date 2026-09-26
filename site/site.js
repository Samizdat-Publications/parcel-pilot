// Parcel Pilot landing page: clips that play while on screen, the whole-shift player's
// timeline, the island postcards, the sound board and the greybox slider. The page reads
// fine without any of this.
(function () {
	'use strict';

	const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	const conn = navigator.connection || {};
	const saveData = !!conn.saveData || /(^|-)2g|3g/.test(conn.effectiveType || '');
	const quiet = reduceMotion || saveData;

	// ------------------------------------------------------------ top bar
	const topbar = document.getElementById('topbar');
	const hero = document.getElementById('top');
	if (topbar && hero && 'IntersectionObserver' in window) {
		new IntersectionObserver(([entry]) => topbar.classList.toggle('solid', !entry.isIntersecting), {
			rootMargin: '-72px 0px 0px 0px',
		}).observe(hero);
	}

	// ------------------------------------------------------------ hero reel
	const heroVideo = document.getElementById('hero-video');
	const heroToggle = document.getElementById('hero-toggle');
	function setHero(playing) {
		if (!heroVideo) return;
		if (playing) {
			heroVideo.play().catch(() => setHero(false));
		} else {
			heroVideo.pause();
		}
		heroToggle.textContent = playing ? 'Pause the reel' : 'Play the reel';
		heroToggle.setAttribute('aria-pressed', String(!playing));
	}
	if (heroVideo) {
		setHero(!quiet);
		heroToggle.addEventListener('click', () => setHero(heroVideo.paused));
	}

	// ------------------------------------------------------------ clips that play in view
	function showControls(video) {
		video.controls = true;
		video.removeAttribute('data-inview');
	}
	const clips = document.querySelectorAll('video[data-inview]');
	if (quiet || !('IntersectionObserver' in window)) {
		clips.forEach(showControls);
	} else {
		const watcher = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				const video = entry.target;
				if (entry.isIntersecting) {
					video.preload = 'auto';
					video.play().catch((err) => {
						if (err && err.name === 'NotAllowedError') showControls(video);
					});
				} else {
					video.pause();
				}
			});
		}, { threshold: 0.45 });
		clips.forEach((video) => watcher.observe(video));
	}

	// ------------------------------------------------------------ island postcards
	const finePointer = window.matchMedia('(pointer: fine)').matches;
	document.querySelectorAll('.island').forEach((card) => {
		const video = card.querySelector('video');
		if (!video) return;
		card.tabIndex = 0;
		card.setAttribute('role', 'button');
		card.setAttribute('aria-label', card.querySelector('h3').textContent + ': play the fly-in');
		const play = () => {
			document.querySelectorAll('.island.playing').forEach((other) => {
				if (other !== card) stop.call(other);
			});
			video.preload = 'auto';
			video.play().then(() => card.classList.add('playing')).catch(() => undefined);
		};
		function stop() {
			const v = this.querySelector('video');
			v.pause();
			this.classList.remove('playing');
		}
		if (finePointer && !reduceMotion) {
			card.addEventListener('mouseenter', play);
			card.addEventListener('mouseleave', () => stop.call(card));
		}
		card.addEventListener('click', () => (video.paused ? play() : stop.call(card)));
		card.addEventListener('keydown', (e) => {
			if (e.key === 'Enter' || e.key === ' ') {
				e.preventDefault();
				video.paused ? play() : stop.call(card);
			}
		});
	});

	// ------------------------------------------------------------ the whole shift
	const shift = document.getElementById('shift');
	const ticks = document.getElementById('tl-ticks');
	const fill = document.getElementById('tl-fill');
	const now = document.getElementById('now');
	const timeline = document.getElementById('timeline');

	function describe(ev) {
		switch (ev.kind) {
			case 'go': return 'Go! The first parcel is on its way';
			case 'delivery': {
				const [grade, island, points] = ev.label.split('|');
				return grade + ' to ' + island + ', +' + points + ' points';
			}
			case 'stamp': return 'A stamp: +25 points and 3 seconds';
			case 'ring': return 'Boost ring: the meter tops up';
			case 'zap': return 'Zapped by a thundercloud: parcel damaged';
			case 'crash': return 'A bump: parcel damaged, the combo breaks';
			case 'results': return 'Time! The shift report: ' + ev.label;
			default: return '';
		}
	}

	function fmt(t) {
		const s = Math.max(0, Math.round(t));
		return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
	}

	if (shift && ticks) {
		fetch('media/chapters.json').then((r) => (r.ok ? r.json() : Promise.reject(r.status))).then((data) => {
			const duration = data.duration;
			const events = data.events.filter((ev, i, all) => !(ev.kind === 'crash'
				&& all.some((o) => o.kind === 'zap' && Math.abs(o.t - ev.t) < 0.2)));
			const buttons = events.map((ev) => {
				const b = document.createElement('button');
				b.type = 'button';
				b.className = 'tick k-' + ev.kind;
				b.style.left = (100 * ev.t / duration).toFixed(3) + '%';
				b.title = fmt(ev.t) + '  ' + describe(ev);
				b.setAttribute('aria-label', fmt(ev.t) + ', ' + describe(ev));
				b.addEventListener('click', () => {
					shift.preload = 'auto';
					shift.currentTime = Math.max(0, ev.t - 1.5);
					shift.play().catch(() => undefined);
				});
				ticks.appendChild(b);
				return b;
			});
			timeline.hidden = false;
			document.getElementById('legend').hidden = false;

			let shown = -1;
			shift.addEventListener('timeupdate', () => {
				const t = shift.currentTime;
				fill.style.width = (100 * t / duration).toFixed(2) + '%';
				let latest = -1;
				events.forEach((ev, i) => {
					buttons[i].classList.toggle('past', ev.t <= t);
					// Name an event from just before it happens (a tick seeks 1.5 s early) until 4.5 s after.
					if (ev.t <= t + 1.6 && t - ev.t < 4.5) latest = i;
				});
				if (latest !== shown) {
					shown = latest;
					now.textContent = latest >= 0 ? fmt(events[latest].t) + '  ' + describe(events[latest]) : '';
				}
			});

			const st = data.stats || {};
			const report = document.getElementById('report');
			const rows = [['Score', st.score], ['Deliveries', st.deliveries], ['Best streak', st.streak],
				['Rank', st.rank], ['Length', fmt(duration)]];
			rows.filter((row) => row[1] !== undefined && row[1] !== '').forEach(([label, value]) => {
				const box = document.createElement('div');
				const dt = document.createElement('dt');
				const dd = document.createElement('dd');
				dt.textContent = label;
				dd.textContent = value;
				box.append(dt, dd);
				report.appendChild(box);
			});
			report.hidden = false;
		}).catch(() => undefined);
	}

	// ------------------------------------------------------------ sound board
	const board = document.getElementById('soundboard');
	const scope = document.getElementById('scope');
	if (board && scope) {
		const ctx2d = scope.getContext('2d');
		const audio = new Audio();
		audio.preload = 'none';
		let current = null;
		let analyser = null;
		let data = null;
		let raf = 0;

		function drawIdle() {
			const w = scope.width;
			const h = scope.height;
			ctx2d.clearRect(0, 0, w, h);
			ctx2d.strokeStyle = 'rgba(255, 201, 61, 0.55)';
			ctx2d.lineWidth = 2;
			ctx2d.beginPath();
			ctx2d.moveTo(0, h / 2);
			ctx2d.lineTo(w, h / 2);
			ctx2d.stroke();
		}

		function draw() {
			const w = scope.width;
			const h = scope.height;
			analyser.getByteTimeDomainData(data);
			ctx2d.clearRect(0, 0, w, h);
			ctx2d.strokeStyle = '#ffc93d';
			ctx2d.lineWidth = 2.5;
			ctx2d.beginPath();
			for (let i = 0; i < data.length; i++) {
				const x = (i / (data.length - 1)) * w;
				const y = (data[i] / 255) * h;
				if (i === 0) ctx2d.moveTo(x, y); else ctx2d.lineTo(x, y);
			}
			ctx2d.stroke();
			raf = requestAnimationFrame(draw);
		}

		function stop() {
			audio.pause();
			if (current) current.classList.remove('on');
			current = null;
			cancelAnimationFrame(raf);
			drawIdle();
		}

		function ensureAnalyser() {
			if (analyser || !(window.AudioContext || window.webkitAudioContext)) return;
			try {
				const ac = new (window.AudioContext || window.webkitAudioContext)();
				const source = ac.createMediaElementSource(audio);
				analyser = ac.createAnalyser();
				analyser.fftSize = 2048;
				data = new Uint8Array(analyser.fftSize);
				source.connect(analyser);
				analyser.connect(ac.destination);
				audio.addEventListener('play', () => ac.resume());
			} catch (e) {
				analyser = null;
			}
		}

		board.addEventListener('click', (e) => {
			const chip = e.target.closest('.chip');
			if (!chip) return;
			if (chip === current) {
				stop();
				return;
			}
			stop();
			ensureAnalyser();
			current = chip;
			chip.classList.add('on');
			audio.loop = chip.dataset.sound === 'music';
			audio.src = 'media/sound/' + chip.dataset.sound + '.m4a';
			audio.play().then(() => {
				if (analyser && !reduceMotion) draw();
			}).catch(() => stop());
		});
		audio.addEventListener('ended', stop);
		drawIdle();
	}

	// ------------------------------------------------------------ greybox slider
	const slider = document.getElementById('slider');
	const range = document.getElementById('compare-range');
	const after = document.getElementById('compare-after');
	const label = document.getElementById('compare-label');
	if (slider && range) {
		const set = () => slider.style.setProperty('--pos', range.value + '%');
		range.addEventListener('input', set);
		set();
		const names = { 2: 'M2 art pass', 3: 'M3 juice', 4: 'M4 finished' };
		document.querySelectorAll('.tabs [role="tab"]').forEach((tab) => {
			tab.addEventListener('click', () => {
				document.querySelectorAll('.tabs [role="tab"]').forEach((t) => t.setAttribute('aria-selected', String(t === tab)));
				after.src = 'media/m' + tab.dataset.m + '.jpg';
				label.textContent = names[tab.dataset.m];
			});
		});
	}

	// Enter jumps straight into the game, as on its title screen.
	document.addEventListener('keydown', (e) => {
		if (e.key === 'Enter' && !e.repeat && e.target === document.body) location.href = 'play/';
	});
}());
