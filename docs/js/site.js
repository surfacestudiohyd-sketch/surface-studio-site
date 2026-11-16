/* Surface Studio - site behaviour. External file so the Content-Security-Policy can forbid inline scripts. */
(function () {
  'use strict';
  // Hero typing effect. The full phrase "Precision Coated." is already in the HTML for crawlers / no-JS.
  var words = ['Precision Coated.', 'Beyond Paint.', 'Flawless Finishes.', 'Engineered Surfaces.'];
  var w = 0, c = words[0].length, del = false, p = 0, el = document.getElementById('typed');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (el && !reduce) {
    setInterval(function () {
      var s = words[w];
      if (!del) { if (c < s.length) { c++; } else if (++p > 22) { p = 0; del = true; } }
      else { if (c > 0) { c--; } else { del = false; w = (w + 1) % words.length; } }
      el.textContent = s.slice(0, c);
    }, 85);
  }

  // Quote form -> WhatsApp. User input only goes into the URL (encodeURIComponent), never into the DOM.
  var fm = document.getElementById('enquiry');
  if (fm) {
    fm.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = fm.elements;
      var v = function (n, max) { var x = f.namedItem(n); return x ? String(x.value || '').trim().slice(0, max) : ''; };
      var t = 'Hi Surface Studio, I would like a quote.' +
        '\nName: ' + v('name', 80) + '\nPhone: ' + v('phone', 20) +
        '\nRequirement: ' + v('need', 80) + '\nDetails: ' + v('msg', 1000);
      window.open('https://wa.me/919505969558?text=' + encodeURIComponent(t), '_blank', 'noopener');
    });
  }

  // Open / closed status in India time (studio hours Mon-Sat 9:30-17:30).
  var on = document.getElementById('open-now');
  if (on) {
    try {
      var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
      var g = function (t) { for (var i = 0; i < parts.length; i++) if (parts[i].type === t) return parts[i].value; return ''; };
      var day = g('weekday'), mins = (+g('hour') % 24) * 60 + (+g('minute'));
      var isOpen = day !== 'Sun' && mins >= 570 && mins < 1050;
      on.textContent = isOpen ? 'Open now \u00B7 until 5:30 pm' : 'Closed now \u00B7 Mon \u2013 Sat, 9:30 am \u2013 5:30 pm';
    } catch (e) {}
  }
  var firstFaq = document.querySelector('.ss-faq');
  if (firstFaq) firstFaq.setAttribute('open', '');

  // Mobile menu: close on link click, outside click and Escape.
  var mob = document.querySelector('.ss-mob');
  if (mob) {
    mob.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { mob.removeAttribute('open'); }); });
    document.addEventListener('click', function (e) { if (mob.hasAttribute('open') && !mob.contains(e.target)) mob.removeAttribute('open'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mob.hasAttribute('open')) { mob.removeAttribute('open'); mob.querySelector('summary').focus(); }
    });
  }

  // Brand tabs (WAI-ARIA tabs pattern: click, Arrow keys, Home / End).
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.ss-tab'));
  function select(b, focus) {
    tabs.forEach(function (x) {
      var on = x === b;
      x.setAttribute('aria-selected', on ? 'true' : 'false');
      x.tabIndex = on ? 0 : -1;
    });
    document.querySelectorAll('[data-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== b.getAttribute('data-tab'); });
    if (focus) b.focus();
  }
  tabs.forEach(function (b, i) {
    b.addEventListener('click', function () { select(b, false); });
    b.addEventListener('keydown', function (e) {
      var n = null;
      if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') n = tabs[0];
      else if (e.key === 'End') n = tabs[tabs.length - 1];
      if (n) { e.preventDefault(); select(n, true); }
    });
  });
})();
