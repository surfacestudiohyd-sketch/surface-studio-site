/* Surface Studio - instant quote from a cutlist.
   Everything runs in the visitor's browser: the file is never uploaded anywhere.
   Rates come from the studio's Zoho Books rate card (pre-GST), injected at build time. */
(function () {
  'use strict';
  var RATES = {"source":"Zoho Books item rates","gst":18,"rates":{"paint|Axalta|Glossy":{"rft":90.0,"sft":320.0},"paint|Axalta|Matte":{"rft":80.0,"sft":300.0},"paint|Axalta|Metallic":{"rft":160.0,"sft":400.0},"paint|Axalta|Pearl":{"rft":170.0,"sft":500.0},"paint|ICA|Glossy":{"rft":110.0,"sft":340.0},"paint|ICA|Matte":{"rft":100.0,"sft":320.0},"paint|Sirca|Glossy":{"rft":110.0,"sft":340.0},"paint|Sirca|Matte":{"rft":100.0,"sft":320.0},"polish|Axalta|Glossy|Coloured":{"rft":95.0,"sft":235.0},"polish|Axalta|Glossy|Natural":{"rft":90.0,"sft":230.0},"polish|Axalta|Matte|Coloured":{"rft":85.0,"sft":215.0},"polish|Axalta|Matte|Natural":{"rft":80.0,"sft":210.0},"polish|ICA|Glossy|Coloured":{"rft":95.0,"sft":245.0},"polish|ICA|Glossy|Natural":{"rft":90.0,"sft":240.0},"polish|ICA|Matte|Coloured":{"rft":85.0,"sft":225.0},"polish|ICA|Matte|Natural":{"rft":80.0,"sft":220.0},"polish|Sirca|Glossy|Coloured":{"rft":95.0,"sft":245.0},"polish|Sirca|Glossy|Natural":{"rft":90.0,"sft":240.0},"polish|Sirca|Matte|Coloured":{"rft":85.0,"sft":225.0},"polish|Sirca|Matte|Natural":{"rft":80.0,"sft":220.0}}};
  var MM2_PER_SQFT = 92903.04, MM_PER_FT = 304.8;
  var STRIP_MM = 152.4;        // strips up to 6 inches wide are charged per running foot
  var STRIP_TXT = '6 in';
  var MAX_BYTES = 5 * 1024 * 1024, MAX_ROWS = 3000;
  var WA = '919505969558';

  var $ = function (id) { return document.getElementById(id); };
  var fileIn = $('cl-file'), drop = $('cl-drop'), statusEl = $('cl-status'), out = $('cl-result');
  if (!fileIn || !out) return;
  var work = $('cl-work'), brand = $('cl-brand'), finish = $('cl-finish'), tone = $('cl-tone'), sides = $('cl-sides'), design = $('cl-design');
  function dfac() { var d = parseFloat(design && design.value); return d > 1 ? d : 1; }
  var state = { rows: null, name: '', hash: '' };

  /* ---------- helpers ---------- */
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'text') e.textContent = attrs[k];
      else if (k === 'style') e.style.cssText = attrs[k];
      else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return e;
  }
  function inr(n) { return '₹' + Math.round(n).toLocaleString('en-IN'); }
  function num(n, d) { return Number(n).toLocaleString('en-IN', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function say(msg, bad) { statusEl.textContent = msg; statusEl.style.color = bad ? '#FCA5A5' : '#A9A9B3'; }
  function hash(str) { // FNV-1a, base-36: same cutlist + same options -> same quote code
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h.toString(36).toUpperCase().padStart(6, '0').slice(-6);
  }

  /* ---------- CSV ---------- */
  function parseCSV(text) {
    var first = text.split(/\r?\n/, 1)[0] || '';
    var delim = [',', '\t', ';'].sort(function (a, b) { return first.split(b).length - first.split(a).length; })[0];
    var rows = [], row = [], cell = '', q = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (q) {
        if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
        else cell += ch;
      } else if (ch === '"') q = true;
      else if (ch === delim) { row.push(cell); cell = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(cell); rows.push(row); row = []; cell = '';
        if (rows.length > MAX_ROWS + 50) break;
      } else cell += ch;
    }
    if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }

  /* ---------- XLSX (zip + XML, no libraries) ---------- */
  function u16(b, o) { return b[o] | (b[o + 1] << 8); }
  function u32(b, o) { return (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16) | (b[o + 3] << 24)) >>> 0; }
  function unzip(buf) {
    var b = new Uint8Array(buf), eocd = -1;
    for (var i = b.length - 22; i >= Math.max(0, b.length - 66000); i--) { if (u32(b, i) === 0x06054b50) { eocd = i; break; } }
    if (eocd < 0) throw new Error('not a valid .xlsx file');
    var n = u16(b, eocd + 10), p = u32(b, eocd + 16), files = {};
    var dec = new TextDecoder();
    for (var k = 0; k < n; k++) {
      if (u32(b, p) !== 0x02014b50) break;
      var method = u16(b, p + 10), csize = u32(b, p + 20), nlen = u16(b, p + 28), xlen = u16(b, p + 30), clen = u16(b, p + 32), lho = u32(b, p + 42);
      var name = dec.decode(b.subarray(p + 46, p + 46 + nlen));
      var start = lho + 30 + u16(b, lho + 26) + u16(b, lho + 28);
      files[name] = { method: method, data: b.subarray(start, start + csize) };
      p += 46 + nlen + xlen + clen;
    }
    return files;
  }
  function inflate(f) {
    if (f.method === 0) return Promise.resolve(new TextDecoder().decode(f.data));
    if (f.method !== 8 || typeof DecompressionStream === 'undefined') return Promise.reject(new Error('this browser cannot read .xlsx - please save the sheet as CSV'));
    var stream = new Blob([f.data]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
    return new Response(stream).text();
  }
  function colIndex(ref) { var m = /^([A-Z]+)/.exec(ref || ''), n = 0; if (!m) return -1; for (var i = 0; i < m[1].length; i++) n = n * 26 + m[1].charCodeAt(i) - 64; return n - 1; }
  function parseXLSX(buf) {
    var files = unzip(buf), xml = function (s) { return new DOMParser().parseFromString(s, 'application/xml'); };
    var sheetPath = 'xl/worksheets/sheet1.xml';
    var wb = files['xl/workbook.xml'], rels = files['xl/_rels/workbook.xml.rels'];
    var chain = Promise.resolve();
    if (wb && rels) {
      chain = Promise.all([inflate(wb), inflate(rels)]).then(function (r) {
        var s = xml(r[0]).getElementsByTagName('sheet')[0], rid = s && (s.getAttribute('r:id') || s.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'id'));
        Array.prototype.forEach.call(xml(r[1]).getElementsByTagName('Relationship'), function (x) {
          if (x.getAttribute('Id') === rid) { var t = x.getAttribute('Target').replace(/^\//, ''); sheetPath = t.indexOf('xl/') === 0 ? t : 'xl/' + t; }
        });
      });
    }
    var shared = [];
    return chain.then(function () {
      return files['xl/sharedStrings.xml'] ? inflate(files['xl/sharedStrings.xml']) : '';
    }).then(function (s) {
      if (s) Array.prototype.forEach.call(xml(s).getElementsByTagName('si'), function (si) {
        shared.push(Array.prototype.map.call(si.getElementsByTagName('t'), function (t) { return t.textContent; }).join(''));
      });
      if (!files[sheetPath]) throw new Error('could not find the first worksheet');
      return inflate(files[sheetPath]);
    }).then(function (s) {
      var rows = [];
      Array.prototype.forEach.call(xml(s).getElementsByTagName('row'), function (r) {
        if (rows.length > MAX_ROWS + 50) return;
        var row = [];
        Array.prototype.forEach.call(r.getElementsByTagName('c'), function (c) {
          var i = colIndex(c.getAttribute('r')), t = c.getAttribute('t'), v = c.getElementsByTagName('v')[0], val = '';
          if (t === 's' && v) val = shared[+v.textContent] || '';
          else if (t === 'inlineStr') val = Array.prototype.map.call(c.getElementsByTagName('t'), function (x) { return x.textContent; }).join('');
          else if (v) val = v.textContent;
          row[i < 0 ? row.length : i] = val;
        });
        rows.push(row);
      });
      return rows;
    });
  }

  /* ---------- cutlist columns ---------- */
  var SYN = {
    len: ['cleng', 'length', 'len', 'lengthmm', 'l', 'height', 'heightmm', 'h', 'finishlength'],
    wid: ['cwidth', 'width', 'wid', 'widthmm', 'w', 'breadth', 'finishwidth'],
    qty: ['cnt', 'qty', 'quantity', 'nos', 'no', 'count', 'pcs', 'pieces'],
    name: ['name1', 'name', 'part', 'partname', 'description', 'item', 'panel', 'component'],
    mat: ['matname', 'material', 'mat', 'materialname', 'board'],
    thk: ['fthk', 'thk', 'thickness', 'thicknessmm', 't'],
    code: ['barcode', 'code', 'id', 'partid', 'label']
  };
  function norm(s) { return String(s == null ? '' : s).toLowerCase().replace(/[^a-z0-9]/g, ''); }
  function findHeader(rows) {
    for (var r = 0; r < Math.min(rows.length, 25); r++) {
      var map = {}, cells = (rows[r] || []).map(norm);
      Object.keys(SYN).forEach(function (k) {
        for (var s = 0; s < SYN[k].length && map[k] === undefined; s++) {
          var i = cells.indexOf(SYN[k][s]); if (i >= 0) map[k] = i;
        }
      });
      if (map.len !== undefined && map.wid !== undefined) return { row: r, map: map };
    }
    return null;
  }
  function toPanels(rows) {
    var h = findHeader(rows);
    if (!h) throw new Error('could not find Length and Width columns. Use headings like CLENG / CWIDTH or Length / Width (see the sample).');
    var panels = [], skipped = 0;
    for (var r = h.row + 1; r < rows.length && panels.length < MAX_ROWS; r++) {
      var row = rows[r] || [], g = function (k) { return h.map[k] === undefined ? '' : String(row[h.map[k]] == null ? '' : row[h.map[k]]).trim(); };
      var L = parseFloat(g('len').replace(/,/g, '')), W = parseFloat(g('wid').replace(/,/g, ''));
      if (!(L > 0) || !(W > 0)) { if (row.join('').trim()) skipped++; continue; }
      var q = parseInt(g('qty'), 10); if (!(q > 0)) q = 1;
      panels.push({ name: g('name').slice(0, 60), mat: g('mat').slice(0, 40), thk: g('thk'), code: g('code').slice(0, 30), L: L, W: W, qty: Math.min(q, 500) });
    }
    if (!panels.length) throw new Error('no panel rows with a length and width were found under the headings.');
    return { panels: panels, skipped: skipped, header: rows[h.row].join('|') };
  }

  /* ---------- pricing ---------- */
  function rateKey() {
    var w = work.value, k = w + '|' + brand.value + '|' + finish.value;
    if (w === 'polish') k += '|' + tone.value;
    return k;
  }
  function facesFor(p) {
    var m = p.mat.toUpperCase();
    if (/\bBSL\b|_BSL|BSL_/.test(m)) return { n: 2, why: 'BSL' };
    if (/\bOSL\b|_OSL|OSL_/.test(m)) return { n: 1, why: 'OSL' };
    return { n: +sides.value, why: '' };
  }
  function price() {
    var r = RATES.rates[rateKey()];
    if (!r) return null;
    var res = { sqft: 0, rft: 0, pcs: 0, sqftPanels: 0, rftPanels: 0, flags: [], lines: [], rate: r };
    state.rows.panels.forEach(function (p, i) {
      var f = facesFor(p), shortSide = Math.min(p.L, p.W), longSide = Math.max(p.L, p.W), line = { i: i + 1, p: p, faces: f.n };
      res.pcs += p.qty;
      if (shortSide <= STRIP_MM) {
        line.rft = longSide / MM_PER_FT * p.qty; line.amount = line.rft * r.rft; res.rft += line.rft; res.rftPanels += p.qty;
      } else {
        line.sqft = p.L * p.W * p.qty * f.n / MM2_PER_SQFT; line.amount = line.sqft * r.sft; res.sqft += line.sqft; res.sqftPanels += p.qty;
      }
      var mm = /(\d+)\s*MM/i.exec(p.mat), t = parseFloat(p.thk);
      if (mm && t && +mm[1] !== t) res.flags.push('Row ' + line.i + ': material says ' + mm[1] + 'mm but thickness is ' + t + 'mm');
      if (longSide > 3000) res.flags.push('Row ' + line.i + ': ' + longSide + 'mm is over 3 m, please confirm');
      res.lines.push(line);
    });
    var maxDim = Math.max.apply(null, state.rows.panels.map(function (p) { return Math.max(p.L, p.W); }));
    if (maxDim < 150) res.flags.unshift('All sizes are under 150 - are they in mm? The calculator expects millimetres.');
    res.base = res.sqft * r.sft + res.rft * r.rft;
    res.design = res.base * (dfac() - 1);
    res.sub = res.base + res.design;
    res.gst = res.sub * RATES.gst / 100;
    res.total = res.sub + res.gst;
    return res;
  }
  function label() {
    var w = work.value === 'paint' ? 'PU Paint' : 'PU Polish';
    return w + ' · ' + brand.value + ' · ' + finish.value + (work.value === 'polish' ? ' · ' + tone.value : '');
  }

  /* ---------- options ---------- */
  function syncOptions() {
    var paint = work.value === 'paint', axalta = brand.value === 'Axalta';
    Array.prototype.forEach.call(finish.options, function (o) {
      var special = o.value === 'Metallic' || o.value === 'Pearl';
      o.disabled = special && !(paint && axalta);
      o.hidden = o.disabled;
    });
    if (finish.selectedOptions[0] && finish.selectedOptions[0].disabled) finish.value = 'Matte';
    $('cl-tone-wrap').hidden = paint;
  }

  /* ---------- render ---------- */
  function render() {
    syncOptions();
    if (!state.rows) return;
    var res = price();
    out.textContent = '';
    if (!res) { out.appendChild(el('p', { text: 'That combination is quoted on request. Send us your cutlist on WhatsApp.' })); return; }
    var opts = rateKey() + '|' + sides.value + '|' + dfac();
    var code = 'SSQ-' + new Date().toISOString().slice(2, 10).replace(/-/g, '') + '-' + hash(state.hash + opts);
    var row = function (k, v, strong) {
      return el('div', { style: 'display:flex;justify-content:space-between;gap:16px;padding:9px 0;border-bottom:1px solid #2A2A32' + (strong ? ';font-weight:700;font-size:18px;border-bottom:0' : '') }, [el('span', { text: k, style: strong ? '' : 'color:#C9C9D1' }), el('span', { text: v })]);
    };
    var head = el('div', { style: 'display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px' }, [
      el('h3', { text: 'Estimate', style: 'margin:0;font-size:22px' }),
      el('span', { style: 'font-size:14px;color:#C9C9D1' }, ['Quote code ', el('strong', { text: code, style: 'color:#FF9A3C;letter-spacing:.04em' })])
    ]);
    var rate = res.rate;
    var kids = [head,
      el('p', { text: label() + ' — ' + state.name, style: 'margin:0 0 14px;font-size:14px;color:#A9A9B3;word-break:break-word' }),
      row('Panels', res.pcs + ' pcs (' + state.rows.panels.length + ' rows)')];
    if (res.sqftPanels) kids.push(row('PU area', num(res.sqft, 1) + ' sq ft × ' + inr(rate.sft) + ' = ' + inr(res.sqft * rate.sft)));
    if (res.rftPanels) kids.push(row('Strips up to ' + STRIP_TXT, num(res.rft, 1) + ' rft × ' + inr(rate.rft) + ' = ' + inr(res.rft * rate.rft)));
    if (res.design) kids.push(row('Design work × ' + dfac(), '+ ' + inr(res.design)));
    kids.push(row('Subtotal', inr(res.sub)), row('GST ' + RATES.gst + '%', inr(res.gst)), row('Estimated total', inr(res.total), true));
    if (res.flags.length || state.rows.skipped) {
      var ul = el('ul', { style: 'margin:8px 0 0;padding-left:18px;font-size:13px;line-height:1.6;color:#FCD34D' });
      if (state.rows.skipped) ul.appendChild(el('li', { text: state.rows.skipped + ' row(s) without a valid size were skipped' }));
      res.flags.slice(0, 8).forEach(function (f) { ul.appendChild(el('li', { text: f })); });
      if (res.flags.length > 8) ul.appendChild(el('li', { text: (res.flags.length - 8) + ' more to check' }));
      kids.push(el('div', { style: 'margin-top:14px' }, [el('p', { text: 'Please check', style: 'margin:0;font-weight:600;font-size:14px' }), ul]));
    }
    // panel lines
    var tb = el('tbody');
    res.lines.slice(0, 400).forEach(function (l) {
      tb.appendChild(el('tr', null, [
        el('td', { text: String(l.i) }), el('td', { text: l.p.name || '—' }),
        el('td', { text: l.p.L + ' × ' + l.p.W }), el('td', { text: String(l.p.qty) }),
        el('td', { text: l.sqft !== undefined ? l.faces + (l.faces === 2 ? ' sides' : ' side') : 'strip' }),
        el('td', { text: l.sqft !== undefined ? num(l.sqft, 2) + ' sft' : num(l.rft, 2) + ' rft' }),
        el('td', { text: inr(l.amount) })
      ]));
    });
    var th = el('tr', null, ['#', 'Part', 'Size (mm)', 'Qty', 'Faces', 'Qty (PU)', 'Amount'].map(function (t) { return el('th', { text: t, scope: 'col' }); }));
    var tbl = el('table', { class: 'cl-table' }, [el('thead', null, [th]), tb]);
    kids.push(el('details', { style: 'margin-top:16px' }, [
      el('summary', { text: 'Panel-by-panel breakdown', style: 'cursor:pointer;min-height:44px;display:flex;align-items:center;font-weight:600' }),
      el('div', { style: 'overflow-x:auto;max-height:420px;margin-top:8px' }, [tbl]),
      res.lines.length > 400 ? el('p', { text: 'Showing the first 400 rows.', style: 'font-size:13px;color:#A9A9B3' }) : null
    ]));
    kids.push(el('p', { text: 'This is an estimate from our current rate card (prices before GST, per finished face; strips up to ' + STRIP_TXT + ' wide are charged per running foot; design work such as grooves or profiles is 1.5×). Sides follow the BSL / OSL code in the material column, otherwise your choice above. Edge painting is not included. The final quote follows a panel inspection at our IDA Bollaram studio.', style: 'margin:16px 0 0;font-size:13px;line-height:1.6;color:#A9A9B3' }));
    var msg = 'Hi Surface Studio, I would like to confirm this quote.\nQuote code: ' + code + '\nFinish: ' + label() +
      '\nCutlist: ' + state.name + '\nPanels: ' + res.pcs + ' pcs' + (res.sqftPanels ? '\nPU area: ' + num(res.sqft, 1) + ' sq ft' : '') +
      (res.rftPanels ? '\nStrips: ' + num(res.rft, 1) + ' rft' : '') + (res.design ? '\nDesign work: x' + dfac() : '') + '\nEstimate: ' + inr(res.sub) + ' + GST = ' + inr(res.total) +
      '\n(I will attach the cutlist file here.)';
    var wa = el('a', { href: 'https://wa.me/' + WA + '?text=' + encodeURIComponent(msg), target: '_blank', rel: 'noopener noreferrer', class: 'cl-btn cl-primary' }, ['Send to Surface Studio on WhatsApp']);
    var pr = el('button', { type: 'button', class: 'cl-btn' }, ['Print / save as PDF']);
    pr.addEventListener('click', function () { window.print(); });
    kids.push(el('div', { style: 'display:flex;flex-wrap:wrap;gap:12px;margin-top:20px', class: 'cl-actions' }, [wa, pr]));
    kids.forEach(function (k) { out.appendChild(k); });
    out.hidden = false;
  }

  /* ---------- file handling ---------- */
  function handle(file) {
    if (!file) return;
    out.hidden = true; state.rows = null;
    if (file.size > MAX_BYTES) { say('That file is over 5 MB. Please send it on WhatsApp instead.', true); return; }
    var ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ext === 'pdf' || ext === 'xls') {
      say((ext === 'pdf' ? 'PDF' : 'Old .xls') + ' cutlists cannot be read in the browser. Save it as .xlsx or CSV, or send the file to us on WhatsApp for a quote.', true); return;
    }
    if (['csv', 'tsv', 'txt', 'xlsx'].indexOf(ext) < 0) { say('Please choose a .xlsx or .csv cutlist.', true); return; }
    say('Reading ' + file.name + '…');
    var reader = ext === 'xlsx' ? file.arrayBuffer().then(parseXLSX) : file.text().then(parseCSV);
    reader.then(function (rows) {
      var parsed = toPanels(rows);
      state.rows = parsed; state.name = file.name.slice(0, 80);
      state.hash = parsed.panels.map(function (p) { return [p.code, p.L, p.W, p.qty, p.mat].join(','); }).join(';');
      say('Read ' + parsed.panels.length + ' panel rows from ' + state.name + '. Your file stayed on this device.');
      render();
      out.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    }).catch(function (e) { say('Could not read the file: ' + (e && e.message ? e.message : 'unknown error') + '.', true); });
  }
  fileIn.addEventListener('change', function () { handle(fileIn.files[0]); });
  if (drop) {
    ['dragenter', 'dragover'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.add('cl-over'); }); });
    ['dragleave', 'drop'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.remove('cl-over'); }); });
    drop.addEventListener('drop', function (e) { if (e.dataTransfer && e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]); });
  }
  [work, brand, finish, tone, sides, design].forEach(function (s) { if (s) s.addEventListener('change', render); });

  /* ---------- quick estimate without a cutlist ---------- */
  var sq = $('cl-sqft'), rf = $('cl-rft');
  function manual() {
    var v = Math.min(parseFloat(sq.value) || 0, 100000), l = Math.min(parseFloat(rf && rf.value) || 0, 100000), r = RATES.rates[rateKey()];
    out.textContent = '';
    if (!(v > 0 || l > 0) || !r) { out.hidden = true; return; }
    var base = v * r.sft + l * r.rft, extra = base * (dfac() - 1), sub = base + extra, gst = sub * RATES.gst / 100, total = sub + gst;
    var code = 'SSQ-' + new Date().toISOString().slice(2, 10).replace(/-/g, '') + '-' + hash('manual' + v + '|' + l + '|' + dfac() + rateKey());
    var row = function (k, val, strong) {
      return el('div', { style: 'display:flex;justify-content:space-between;gap:16px;padding:9px 0;border-bottom:1px solid #2A2A32' + (strong ? ';font-weight:700;font-size:18px;border-bottom:0' : '') }, [el('span', { text: k, style: strong ? '' : 'color:#C9C9D1' }), el('span', { text: val })]);
    };
    var msg = 'Hi Surface Studio, I would like a quote.\nQuote code: ' + code + '\nFinish: ' + label() + (v ? '\nApprox. PU area: ' + num(v, 0) + ' sq ft' : '') + (l ? '\nStrips: ' + num(l, 0) + ' rft' : '') + (extra ? '\nDesign work: x' + dfac() : '') + '\nEstimate: ' + inr(sub) + ' + GST = ' + inr(total);
    var kids = [el('div', { style: 'display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px' }, [
        el('h3', { text: 'Quick estimate', style: 'margin:0;font-size:22px' }),
        el('span', { style: 'font-size:14px;color:#C9C9D1' }, ['Quote code ', el('strong', { text: code, style: 'color:#FF9A3C;letter-spacing:.04em' })])]),
      el('p', { text: label(), style: 'margin:0 0 14px;font-size:14px;color:#A9A9B3' })];
    if (v) kids.push(row('PU area', num(v, 0) + ' sq ft × ' + inr(r.sft) + ' = ' + inr(v * r.sft)));
    if (l) kids.push(row('Strips up to ' + STRIP_TXT, num(l, 0) + ' rft × ' + inr(r.rft) + ' = ' + inr(l * r.rft)));
    if (extra) kids.push(row('Design work × ' + dfac(), '+ ' + inr(extra)));
    kids.push(row('Subtotal', inr(sub)), row('GST ' + RATES.gst + '%', inr(gst)), row('Estimated total', inr(total), true),
      el('p', { text: 'A rough guide from our rate card, per finished face. Edge painting is not included. The final quote follows a panel inspection.', style: 'margin:14px 0 0;font-size:13px;line-height:1.6;color:#A9A9B3' }),
      el('div', { style: 'display:flex;flex-wrap:wrap;gap:12px;margin-top:18px', class: 'cl-actions' }, [
        el('a', { href: 'https://wa.me/' + WA + '?text=' + encodeURIComponent(msg), target: '_blank', rel: 'noopener noreferrer', class: 'cl-btn cl-primary' }, ['Send to Surface Studio on WhatsApp'])]));
    kids.forEach(function (k) { out.appendChild(k); });
    out.hidden = false;
  }
  if (sq) {
    [sq, rf].forEach(function (x) { if (x) x.addEventListener('input', function () { state.rows = null; say('No file chosen yet.'); manual(); }); });
    [work, brand, finish, tone, design].forEach(function (x) { if (x) x.addEventListener('change', function () { if (!state.rows && (sq.value || (rf && rf.value))) manual(); }); });
    fileIn.addEventListener('change', function () { sq.value = ''; if (rf) rf.value = ''; });
  }

  // Sample cutlist download (same columns as factory panel lists)
  var sample = $('cl-sample');
  if (sample) sample.addEventListener('click', function () {
    var csv = 'NAME1,MATNAME,CLENG,CWIDTH,CNT,BARCODE,FTHK\n' +
      'Shutter Left,HDHMR_BSL_18MM,2100,450,2,P0001,18\n' +
      'Shutter Right,HDHMR_BSL_18MM,2100,450,2,P0002,18\n' +
      'Loft Shutter,HDHMR_BSL_18MM,600,450,4,P0003,18\n' +
      'End Panel,HDHMR_OSL_18MM,2400,580,2,P0004,18\n' +
      'Skirting,HDHMR_OSL_18MM,2400,80,3,P0005,18\n';
    var url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    var a = el('a', { href: url, download: 'surface-studio-cutlist-sample.csv' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  syncOptions();
})();
