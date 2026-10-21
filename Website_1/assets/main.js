// TCM Tuina Massage: kleine Helfer ohne Bibliotheken.
// Ohne JavaScript bleibt alles lesbar: Inhalte sind sichtbar, Buchungslinks führen zu /booking/.
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Abschnitte erscheinen einmal, ihre Teile nacheinander.
  var groups = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    root.classList.add('js');
    groups.forEach(function (g) {
      Array.prototype.forEach.call(g.children, function (child, i) { child.style.setProperty('--i', Math.min(i, 6)); });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    groups.forEach(function (g) { io.observe(g); });
  }

  // Das Menü schließt sich nach einem Klick auf einen Eintrag, außerhalb des Menüs oder mit Escape.
  var menu = document.querySelector('.menu');
  if (menu) {
    document.addEventListener('click', function (e) {
      if (!menu.open) return;
      if (e.target.closest('.menu-panel a') || !menu.contains(e.target)) menu.open = false;
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
    });
  }

  // Bei reduzierter Bewegung bleibt der Clip als Standbild stehen.
  if (reduce) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) { v.removeAttribute('autoplay'); v.pause(); });
  }

  // Die historischen Tafeln im Kreis wechseln langsam.
  var chart = document.querySelector('[data-crossfade]');
  if (chart && !reduce) {
    var imgs = chart.querySelectorAll('img');
    var n = 0, timer = null;
    imgs[0].classList.add('is-on');
    var step = function () {
      imgs[n].classList.remove('is-on');
      n = (n + 1) % imgs.length;
      imgs[n].classList.add('is-on');
    };
    var start = function () { if (!timer) timer = setInterval(step, 6000); };
    var stop = function () { clearInterval(timer); timer = null; };
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
    start();
  }

  // Heute geöffnet? Nach Münchner Zeit, aus den Behandlungszeiten der Praxis.
  var today = document.querySelector('[data-today]');
  if (today && window.Intl) {
    var hours = { 0: [13, 16], 1: [10, 18], 2: [10, 18], 3: [10, 18], 4: [10, 18], 5: [10, 18] };
    var names = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
    var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Berlin', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false }).formatToParts(new Date());
    var get = function (t) { var p = parts.find(function (x) { return x.type === t; }); return p ? p.value : ''; };
    var day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday'));
    var now = parseInt(get('hour'), 10) + parseInt(get('minute'), 10) / 60;
    var h = hours[day];
    var text;
    if (h && now >= h[0] && now < h[1]) {
      text = 'Heute Termine bis ' + h[1] + ' Uhr';
      today.classList.add('is-open');
    } else if (h && now < h[0]) {
      text = 'Heute Termine ab ' + h[0] + ' Uhr';
    } else {
      var d = day, next;
      for (var k = 1; k <= 7; k++) { d = (day + k) % 7; if (hours[d]) { next = d; break; } }
      text = 'Nächste Termine ' + (next === (day + 1) % 7 ? 'morgen' : 'am ' + names[next]) + ' ab ' + hours[next][0] + ' Uhr';
    }
    today.textContent = text;
    today.hidden = false;
  }

  // Online-Buchung (cituro) im Fenster. Das iframe lädt erst nach dem Klick.
  var dialog = document.getElementById('booking');
  if (dialog && typeof dialog.showModal === 'function') {
    var frame = dialog.querySelector('iframe');
    var pick = dialog.querySelector('.booking-pick');
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-booking]');
      if (trigger) {
        e.preventDefault();
        if (!frame.getAttribute('src')) frame.setAttribute('src', frame.dataset.src);
        // Kommt der Klick von einer Preiskachel, nennt das Fenster die gewählte Massage.
        // cituro zeigt immer alle Leistungen, deshalb der Hinweis, welchen Eintrag man wählt.
        if (pick) {
          if (trigger.dataset.pick) {
            pick.innerHTML = 'Ihre Wahl: <b>' + trigger.dataset.pickInfo + '</b>. Wählen Sie in der Liste „TCM Tuina Massage - ' + trigger.dataset.pick + '“.';
            pick.hidden = false;
          } else {
            pick.hidden = true;
          }
        }
        dialog.showModal();
        return;
      }
      if (e.target.closest('[data-booking-close]') || e.target === dialog) dialog.close();
    });
  }
})();
