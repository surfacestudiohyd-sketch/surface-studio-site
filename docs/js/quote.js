/* Surface Studio - instant quote calculator (v2).
   One editable panel table. Rows come from an uploaded cutlist (.xlsx / .csv) or are typed in
   from drawings. Each panel is priced like the studio's Zoho quotes:
     area  = length x width x qty x finished faces            (per sq ft)
     edges = full perimeter x qty, when "Edges" is ticked      (per running ft)
     design work (grooves, profiles, CNC) = 1.5x on that panel
   Everything runs in the visitor's browser. Files are never uploaded anywhere.
   Rates (pre-GST) come from the Zoho Books rate card, injected at build time. */
(function () {
  'use strict';
  var RATES = {"source":"Zoho Books item rates","gst":18,"rates":{"paint|Axalta|Glossy":{"rft":90.0,"sft":320.0},"paint|Axalta|Matte":{"rft":80.0,"sft":300.0},"paint|Axalta|Metallic":{"rft":160.0,"sft":400.0},"paint|Axalta|Pearl":{"rft":170.0,"sft":500.0},"paint|ICA|Glossy":{"rft":110.0,"sft":340.0},"paint|ICA|Matte":{"rft":100.0,"sft":320.0},"paint|Sirca|Glossy":{"rft":110.0,"sft":340.0},"paint|Sirca|Matte":{"rft":100.0,"sft":320.0},"polish|Axalta|Glossy|Coloured":{"rft":95.0,"sft":235.0},"polish|Axalta|Glossy|Natural":{"rft":90.0,"sft":230.0},"polish|Axalta|Matte|Coloured":{"rft":85.0,"sft":215.0},"polish|Axalta|Matte|Natural":{"rft":80.0,"sft":210.0},"polish|ICA|Glossy|Coloured":{"rft":95.0,"sft":245.0},"polish|ICA|Glossy|Natural":{"rft":90.0,"sft":240.0},"polish|ICA|Matte|Coloured":{"rft":85.0,"sft":225.0},"polish|ICA|Matte|Natural":{"rft":80.0,"sft":220.0},"polish|Sirca|Glossy|Coloured":{"rft":95.0,"sft":245.0},"polish|Sirca|Glossy|Natural":{"rft":90.0,"sft":240.0},"polish|Sirca|Matte|Coloured":{"rft":85.0,"sft":225.0},"polish|Sirca|Matte|Natural":{"rft":80.0,"sft":220.0}},"ai_endpoint":""};
  var MM2_PER_SQFT = 92903.04, MM_PER_FT = 304.8, MM_PER_IN = 25.4;
  var DESIGN_X = 1.5;
  var MAX_BYTES = 5 * 1024 * 1024, MAX_ROWS = 1500, MAX_DRAWINGS = 10, MAX_DRAWING_BYTES = 20 * 1024 * 1024;
  var WA = '919505969558';

  var $ = function (id) { return document.getElementById(id); };
  var fileIn = $('cl-file'), drop = $('cl-drop'), statusEl = $('cl-status'), out = $('cl-result');
  var body = $('cl-rows'), tableWrap = $('cl-table-wrap');
  if (!fileIn || !out || !body) return;
  var work = $('cl-work'), brand = $('cl-brand'), finish = $('cl-finish'), tone = $('cl-tone'), sides = $('cl-sides'), unit = $('cl-unit');
  var drawIn = $('cl-drawings'), drawList = $('cl-drawing-list');

  var rows = [];          // { name, L, W, qty, faces, edges, design }  (L, W always in mm)
  var drawings = [];      // { name, size, url, isImg }
  var source = '';        // cutlist file name, if any
  var skipped = 0;

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
  function hash(str) {
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h.toString(36).toUpperCase().padStart(6, '0').slice(-6);
  }
  function unitMM() { return unit && unit.value === 'in' ? MM_PER_IN : 1; }
  function fromMM(v) { return Math.round(v / unitMM() * 100) / 100; }

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
    code: ['barcode', 'code', 'id', 'partid', 'label'],
    design: ['design', 'designwork', 'groove', 'grooves', 'profile'],
    edges: ['edges', 'edge', 'edgepaint', 'edgepainting']
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
      panels.push({ name: g('name').slice(0, 60), mat: g('mat').slice(0, 40), thk: g('thk'), code: g('code').slice(0, 30), L: L, W: W, qty: Math.min(q, 500),
        design: /^(y|yes|true|1)$/i.test(g('design')), edges: !/^(n|no|false|0)$/i.test(g('edges')) });
    }
    if (!panels.length) throw new Error('no panel rows with a length and width were found under the headings.');
    return { panels: panels, skipped: skipped, header: rows[h.row].join('|') };
  }


  /* ---------- PDF panel lists (pdf.js, loaded only when a PDF is chosen) ---------- */
  var pdfjsPromise = null;
  function loadPdfjs() {
    if (!pdfjsPromise) {
      pdfjsPromise = import('/js/vendor/pdf.min.mjs').then(function (m) {
        m.GlobalWorkerOptions.workerSrc = '/js/vendor/pdf.worker.min.mjs';
        return m;
      });
    }
    return pdfjsPromise;
  }
  // Turn each PDF page into rows of cells. Text items are grouped into lines by their y position,
  // then each item is placed in the column whose header (CLENG, CWIDTH, ...) is closest in x.
  function pdfToRows(buf) {
    return loadPdfjs().then(function (pdfjs) {
      return pdfjs.getDocument({ data: new Uint8Array(buf), isEvalSupported: false }).promise;
    }).then(function (doc) {
      if (doc.numPages > 60) throw new Error('that PDF has more than 60 pages');
      var jobs = [];
      for (var i = 1; i <= doc.numPages; i++) jobs.push(doc.getPage(i).then(function (p) { return p.getTextContent(); }));
      return Promise.all(jobs);
    }).then(function (pages) {
      var all = [], header = null;
      pages.forEach(function (tc) {
        var lines = [];
        tc.items.forEach(function (it) {
          var t = (it.str || '').trim(); if (!t) return;
          var x = it.transform[4], y = it.transform[5], line = null;
          for (var k = 0; k < lines.length; k++) if (Math.abs(lines[k].y - y) < 3) { line = lines[k]; break; }
          if (!line) { line = { y: y, items: [] }; lines.push(line); }
          line.items.push({ x: x, w: it.width || 0, t: t });
        });
        lines.sort(function (a, b) { return b.y - a.y; });
        lines.forEach(function (ln) {
          ln.items.sort(function (a, b) { return a.x - b.x; });
          var cells = ln.items.map(function (i) { return i.t; });
          var normed = cells.map(norm);
          if (normed.indexOf('cleng') >= 0 || (normed.indexOf('length') >= 0 && normed.indexOf('width') >= 0)) {
            header = ln.items.map(function (i) { return { x: i.x + i.w / 2, t: i.t }; });
            if (!all.length) all.push(header.map(function (h) { return h.t; }));
            return;
          }
          if (!header) return;
          var row = header.map(function () { return ''; });
          ln.items.forEach(function (i) {
            var c = i.x + i.w / 2, best = 0, bd = Infinity;
            header.forEach(function (h, k) { var d = Math.abs(h.x - c); if (d < bd) { bd = d; best = k; } });
            row[best] = row[best] ? row[best] + ' ' + i.t : i.t;
          });
          all.push(row);
        });
      });
      if (!all.length) throw new Error('no table with Length / Width (or CLENG / CWIDTH) headings was found. If this is a drawing, use "Read sizes from drawings" below.');
      return all;
    });
  }

  /* ---------- panel table ---------- */
  function facesFromMat(mat, fallback) {
    var m = (mat || '').toUpperCase();
    if (/\bBSL\b|_BSL|BSL_|\(BSL/.test(m)) return 2;
    if (/\bOSL\b|_OSL|OSL_|\(OSL/.test(m)) return 1;
    return fallback;
  }
  function addPanels(list, replace) {
    if (replace) rows = [];
    var seen = {};
    rows.forEach(function (r) { if (r.code) seen[r.code] = 1; });
    list.forEach(function (p) {
      if (rows.length >= MAX_ROWS) return;
      if (p.code && seen[p.code]) return;
      if (p.code) seen[p.code] = 1;
      rows.push({ name: p.name || '', code: p.code || '', mat: p.mat || '', thk: p.thk || '', L: +p.L, W: +p.W,
        qty: Math.max(1, Math.min(500, parseInt(p.qty, 10) || 1)),
        faces: p.faces || facesFromMat(p.mat, +sides.value), edges: p.edges !== false, design: !!p.design });
    });
    drawTable(); render();
  }
  function cellInput(r, key, attrs) {
    var i = el('input', Object.assign({ value: key === 'L' || key === 'W' ? fromMM(r[key]) : r[key], 'aria-label': attrs.label }, attrs.a || {}));
    i.className = 'cl-in' + (attrs.cls ? ' ' + attrs.cls : '');
    i.addEventListener('input', function () {
      if (key === 'name') r.name = i.value.slice(0, 60);
      else if (key === 'qty') r.qty = Math.max(0, Math.min(500, parseInt(i.value, 10) || 0));
      else r[key] = (parseFloat(i.value) || 0) * unitMM();
      render();
    });
    return i;
  }
  function drawTable() {
    body.textContent = '';
    tableWrap.hidden = !rows.length;
    $('cl-rowcount').textContent = rows.length ? rows.length + (rows.length === 1 ? ' panel' : ' panels') : '';
    rows.forEach(function (r, idx) {
      var n = idx + 1;
      var fs = el('select', { 'aria-label': 'Finished sides, panel ' + n, class: 'cl-in cl-sel' }, [el('option', { value: '2', text: '2' }), el('option', { value: '1', text: '1' })]);
      fs.value = String(r.faces);
      fs.addEventListener('change', function () { r.faces = +fs.value; render(); });
      var ed = el('input', { type: 'checkbox', 'aria-label': 'Charge edges, panel ' + n }); ed.checked = r.edges;
      ed.addEventListener('change', function () { r.edges = ed.checked; render(); });
      var dz = el('input', { type: 'checkbox', 'aria-label': 'Design work, panel ' + n }); dz.checked = r.design;
      dz.addEventListener('change', function () { r.design = dz.checked; render(); });
      var del = el('button', { type: 'button', class: 'cl-x', 'aria-label': 'Remove panel ' + n, text: '×' });
      del.addEventListener('click', function () { rows.splice(idx, 1); drawTable(); render(); });
      var amt = el('td', { class: 'cl-amt' });
      r._amt = amt;
      body.appendChild(el('tr', null, [
        el('td', { text: String(n), class: 'cl-n' }),
        el('td', null, [cellInput(r, 'name', { label: 'Part name, panel ' + n, a: { maxlength: '60' }, cls: 'cl-name' })]),
        el('td', null, [cellInput(r, 'L', { label: 'Length, panel ' + n, a: { type: 'number', inputmode: 'decimal', min: '0', step: 'any' } })]),
        el('td', null, [cellInput(r, 'W', { label: 'Width, panel ' + n, a: { type: 'number', inputmode: 'decimal', min: '0', step: 'any' } })]),
        el('td', null, [cellInput(r, 'qty', { label: 'Quantity, panel ' + n, a: { type: 'number', inputmode: 'numeric', min: '0', step: '1' }, cls: 'cl-qty' })]),
        el('td', null, [fs]), el('td', { class: 'cl-c' }, [ed]), el('td', { class: 'cl-c' }, [dz]), amt, el('td', null, [del])
      ]));
    });
  }

  /* ---------- pricing ---------- */
  function rateKey() {
    var k = work.value + '|' + brand.value + '|' + finish.value;
    if (work.value === 'polish') k += '|' + tone.value;
    return k;
  }
  function label() {
    return (work.value === 'paint' ? 'PU Paint' : 'PU Polish') + ' · ' + brand.value + ' · ' + finish.value + (work.value === 'polish' ? ' · ' + tone.value : '');
  }
  function price() {
    var r = RATES.rates[rateKey()];
    if (!r) return null;
    var res = { sqft: 0, rft: 0, pcs: 0, base: 0, design: 0, designPcs: 0, flags: [], rate: r };
    rows.forEach(function (p, i) {
      var sq = p.L * p.W * p.qty * p.faces / MM2_PER_SQFT;
      var rf = p.edges ? 2 * (p.L + p.W) * p.qty / MM_PER_FT : 0;
      var base = sq * r.sft + rf * r.rft, extra = p.design ? base * (DESIGN_X - 1) : 0;
      p._sqft = sq; p._rft = rf; p._amount = base + extra;
      res.sqft += sq; res.rft += rf; res.pcs += p.qty; res.base += base; res.design += extra; if (p.design) res.designPcs += p.qty;
      var mm = /(\d+)\s*MM/i.exec(p.mat), t = parseFloat(p.thk);
      if (mm && t && +mm[1] !== t) res.flags.push('Panel ' + (i + 1) + ': material says ' + mm[1] + 'mm but thickness is ' + t + 'mm');
      if (Math.max(p.L, p.W) > 3050) res.flags.push('Panel ' + (i + 1) + ': ' + Math.round(Math.max(p.L, p.W)) + ' mm is over 10 ft, please confirm');
      if (p.L > 0 && p.W > 0 && Math.max(p.L, p.W) < 150 && unitMM() === 1) res.flags.push('Panel ' + (i + 1) + ': very small, are the sizes in mm?');
    });
    res.sub = res.base + res.design;
    res.gst = res.sub * RATES.gst / 100;
    res.total = res.sub + res.gst;
    return res;
  }

  /* ---------- render ---------- */
  function syncOptions() {
    var paint = work.value === 'paint', axalta = brand.value === 'Axalta';
    Array.prototype.forEach.call(finish.options, function (o) {
      var special = o.value === 'Metallic' || o.value === 'Pearl';
      o.disabled = special && !(paint && axalta); o.hidden = o.disabled;
    });
    if (finish.selectedOptions[0] && finish.selectedOptions[0].disabled) finish.value = 'Matte';
    $('cl-tone-wrap').hidden = paint;
  }
  function render() {
    syncOptions();
    out.textContent = '';
    var live = rows.filter(function (p) { return p.L > 0 && p.W > 0 && p.qty > 0; });
    if (!live.length) { out.hidden = true; rows.forEach(function (p) { if (p._amt) p._amt.textContent = ''; }); return; }
    var res = price();
    if (!res) { out.hidden = false; out.appendChild(el('p', { text: 'That combination is quoted on request. Send us your list on WhatsApp.' })); return; }
    rows.forEach(function (p) { if (p._amt) p._amt.textContent = p.L > 0 && p.W > 0 && p.qty > 0 ? inr(p._amount) : ''; });
    var sig = rows.map(function (p) { return [Math.round(p.L), Math.round(p.W), p.qty, p.faces, p.edges ? 1 : 0, p.design ? 1 : 0].join(','); }).join(';');
    var code = 'SSQ-' + new Date().toISOString().slice(2, 10).replace(/-/g, '') + '-' + hash(sig + '|' + rateKey());
    var row = function (k, v, strong) {
      return el('div', { style: 'display:flex;justify-content:space-between;gap:16px;padding:9px 0;border-bottom:1px solid #2A2A32' + (strong ? ';font-weight:700;font-size:18px;border-bottom:0' : '') }, [el('span', { text: k, style: strong ? '' : 'color:#C9C9D1' }), el('span', { text: v })]);
    };
    var r = res.rate, kids = [
      el('div', { style: 'display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px' }, [
        el('h3', { text: 'Estimate', style: 'margin:0;font-size:22px' }),
        el('span', { style: 'font-size:14px;color:#C9C9D1' }, ['Quote code ', el('strong', { text: code, style: 'color:#FF9A3C;letter-spacing:.04em' })])]),
      el('p', { text: label() + (source ? ' — ' + source : ''), style: 'margin:0 0 14px;font-size:14px;color:#A9A9B3;word-break:break-word' }),
      row('Panels', res.pcs + ' pcs'),
      row('PU area', num(res.sqft, 2) + ' sq ft × ' + inr(r.sft) + ' = ' + inr(res.sqft * r.sft))];
    if (res.rft) kids.push(row('Edges', num(res.rft, 2) + ' rft × ' + inr(r.rft) + ' = ' + inr(res.rft * r.rft)));
    if (res.design) kids.push(row('Design work × ' + DESIGN_X + ' (' + res.designPcs + ' pcs)', '+ ' + inr(res.design)));
    kids.push(row('Subtotal', inr(res.sub)), row('GST ' + RATES.gst + '%', inr(res.gst)), row('Estimated total', inr(res.total), true));
    if (res.flags.length || skipped) {
      var ul = el('ul', { style: 'margin:8px 0 0;padding-left:18px;font-size:13px;line-height:1.6;color:#FCD34D' });
      if (skipped) ul.appendChild(el('li', { text: skipped + ' row(s) without a valid size were skipped' }));
      res.flags.slice(0, 8).forEach(function (f) { ul.appendChild(el('li', { text: f })); });
      if (res.flags.length > 8) ul.appendChild(el('li', { text: (res.flags.length - 8) + ' more to check' }));
      kids.push(el('div', { style: 'margin-top:14px' }, [el('p', { text: 'Please check', style: 'margin:0;font-weight:600;font-size:14px' }), ul]));
    }
    kids.push(el('p', { text: 'Estimate from our current rate card, before GST: area per finished face, edges per running foot around each panel, and design work (grooves, profiles, CNC) at ' + DESIGN_X + '× on the panels ticked. The final quote follows a panel inspection at our IDA Bollaram studio.', style: 'margin:16px 0 0;font-size:13px;line-height:1.6;color:#A9A9B3' }));
    var msg = 'Hi Surface Studio, I would like to confirm this quote.\nQuote code: ' + code + '\nFinish: ' + label() +
      (source ? '\nList: ' + source : '') + '\nPanels: ' + res.pcs + ' pcs\nPU area: ' + num(res.sqft, 2) + ' sq ft' +
      (res.rft ? '\nEdges: ' + num(res.rft, 2) + ' rft' : '') + (res.design ? '\nDesign work: ' + res.designPcs + ' pcs at x' + DESIGN_X : '') +
      '\nEstimate: ' + inr(res.sub) + ' + GST = ' + inr(res.total) +
      (drawings.length ? '\nDrawings: ' + drawings.length + ' file(s), attaching here.' : '') + '\n(I will attach the panel list here.)';
    var wa = el('a', { href: 'https://wa.me/' + WA + '?text=' + encodeURIComponent(msg), target: '_blank', rel: 'noopener noreferrer', class: 'cl-btn cl-primary' }, ['Send to Surface Studio on WhatsApp']);
    var csv = el('button', { type: 'button', class: 'cl-btn' }, ['Download panel list (CSV)']);
    csv.addEventListener('click', downloadCSV);
    var pr = el('button', { type: 'button', class: 'cl-btn' }, ['Print / save as PDF']);
    pr.addEventListener('click', function () { window.print(); });
    kids.push(el('div', { style: 'display:flex;flex-wrap:wrap;gap:12px;margin-top:20px', class: 'cl-actions' }, [wa, csv, pr]));
    kids.forEach(function (k) { out.appendChild(k); });
    out.hidden = false;
  }
  function csvCell(v) { v = String(v == null ? '' : v); if (/^[=+\-@]/.test(v)) v = "'" + v; return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function downloadCSV() {
    var lines = [['NAME1', 'MATNAME', 'CLENG', 'CWIDTH', 'CNT', 'FACES', 'EDGES', 'DESIGN', 'BARCODE', 'SQFT', 'RFT', 'AMOUNT'].join(',')];
    price();
    rows.forEach(function (p) {
      lines.push([p.name, p.mat, Math.round(p.L), Math.round(p.W), p.qty, p.faces, p.edges ? 'Y' : 'N', p.design ? 'Y' : 'N', p.code,
        (p._sqft || 0).toFixed(2), (p._rft || 0).toFixed(2), Math.round(p._amount || 0)].map(csvCell).join(','));
    });
    var url = URL.createObjectURL(new Blob([lines.join('\n') + '\n'], { type: 'text/csv' }));
    var a = el('a', { href: url, download: 'surface-studio-panel-list.csv' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /* ---------- cutlist upload ---------- */
  function handle(file) {
    if (!file) return;
    if (file.size > MAX_BYTES) { say('That file is over 5 MB. Please send it on WhatsApp instead.', true); return; }
    var ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ext === 'xls') { say('Old .xls files cannot be read here. Save it as .xlsx, CSV or PDF.', true); return; }
    if (['csv', 'tsv', 'txt', 'xlsx', 'pdf'].indexOf(ext) < 0) { say('Please choose a .xlsx, .csv or .pdf panel list.', true); return; }
    say('Reading ' + file.name + '…');
    var reader = ext === 'xlsx' ? file.arrayBuffer().then(parseXLSX) : ext === 'pdf' ? file.arrayBuffer().then(pdfToRows) : file.text().then(parseCSV);
    reader.then(function (raw) {
      var parsed = toPanels(raw);
      skipped = parsed.skipped;
      source = file.name.slice(0, 80);
      addPanels(parsed.panels.map(function (p) { return { name: p.name, mat: p.mat, thk: p.thk, code: p.code, L: p.L, W: p.W, qty: p.qty, design: p.design, edges: p.edges }; }), true);
      say('Read ' + rows.length + ' panels from ' + source + '. Check the table, tick any panels with design work, and add more rows if needed. Your file stayed on this device.');
      tableWrap.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    }).catch(function (e) { say('Could not read the file: ' + (e && e.message ? e.message : 'unknown error') + '.', true); });
  }
  fileIn.addEventListener('change', function () { handle(fileIn.files[0]); fileIn.value = ''; });
  if (drop) {
    ['dragenter', 'dragover'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.add('cl-over'); }); });
    ['dragleave', 'drop'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.remove('cl-over'); }); });
    drop.addEventListener('drop', function (e) { if (e.dataTransfer && e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]); });
  }

  /* ---------- drawings: read sizes with AI (if the studio has set up the service) ---------- */
  var AI = (RATES.ai_endpoint || '').replace(/\/$/, '');
  function showDrawings() {
    drawList.textContent = '';
    drawings.forEach(function (d, i) {
      var open = el('a', { href: d.url, target: '_blank', rel: 'noopener', class: 'cl-chip' }, [d.isImg ? el('img', { src: d.url, alt: '', width: '40', height: '40' }) : el('span', { class: 'cl-pdf', text: 'PDF' }), el('span', { text: d.name })]);
      var x = el('button', { type: 'button', class: 'cl-x', 'aria-label': 'Remove ' + d.name, text: '×' });
      x.addEventListener('click', function () { URL.revokeObjectURL(d.url); drawings.splice(i, 1); showDrawings(); render(); });
      drawList.appendChild(el('li', null, [open, x]));
    });
  }
  function readDrawing(d) {
    var fd = new FormData();
    fd.append('file', d.file, d.name);
    return fetch(AI + '/read-drawing', { method: 'POST', body: fd }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw new Error(j.error || ('service error ' + r.status));
        return j;
      });
    });
  }
  if (drawIn) drawIn.addEventListener('change', function () {
    var files = Array.prototype.slice.call(drawIn.files || []); drawIn.value = '';
    var added = [];
    files.forEach(function (f) {
      if (drawings.length >= MAX_DRAWINGS) return;
      if (f.size > MAX_DRAWING_BYTES) { say(f.name + ' is over 20 MB; send it on WhatsApp instead.', true); return; }
      var isImg = /^image\/(png|jpe?g|webp)$/.test(f.type), isPdf = f.type === 'application/pdf' || /\.pdf$/i.test(f.name);
      if (!isImg && !isPdf) { say(f.name + ' is not a PDF or image.', true); return; }
      var d = { name: f.name.slice(0, 80), size: f.size, url: URL.createObjectURL(f), isImg: isImg, file: f };
      drawings.push(d); added.push(d);
    });
    showDrawings();
    if (!added.length) return;
    if (!AI) {
      say('Drawings added. Automatic reading is not switched on yet, so send them to us on WhatsApp with your quote code and we will price them.');
      render(); return;
    }
    say('Reading sizes from ' + added.length + ' drawing(s). This can take up to a minute…');
    var found = 0, notes = [];
    added.reduce(function (p, d) {
      return p.then(function () {
        return readDrawing(d).then(function (j) {
          var list = (j.panels || []).filter(function (x) { return x && +x.length_mm > 0 && +x.width_mm > 0; }).slice(0, 400);
          found += list.length;
          if (j.notes) notes.push(d.name + ': ' + String(j.notes).slice(0, 200));
          addPanels(list.map(function (x) {
            return { name: String(x.name || x.unit || '').slice(0, 60), L: +x.length_mm, W: +x.width_mm, qty: x.qty,
              faces: +x.faces === 1 ? 1 : 2, edges: x.edges !== false, design: !!x.design, code: '' };
          }), false);
        }).catch(function (e) { notes.push(d.name + ': ' + (e.message || 'could not be read')); });
      });
    }, Promise.resolve()).then(function () {
      say(found ? 'Read ' + found + ' panels from the drawings. AI reading can miss or misread sizes, so please check every row against the drawing before sending.' + (notes.length ? ' Notes: ' + notes.join(' | ') : '')
                : 'No panel sizes could be read. ' + (notes.join(' | ') || '') + ' Send the drawings on WhatsApp and we will price them.', !found);
    });
  });

  /* ---------- buttons ---------- */
  $('cl-add').addEventListener('click', function () {
    addPanels([{ name: '', L: 0, W: 0, qty: 1 }], false);
    var ins = body.querySelectorAll('tr:last-child input'); if (ins[0]) ins[0].focus();
  });
  $('cl-clear').addEventListener('click', function () { rows = []; source = ''; skipped = 0; drawTable(); render(); say('Table cleared.'); });
  $('cl-all-design').addEventListener('change', function (e) { rows.forEach(function (r) { r.design = e.target.checked; }); drawTable(); render(); });
  if (unit) unit.addEventListener('change', function () { drawTable(); render(); });
  [work, brand, finish, tone].forEach(function (s) { s.addEventListener('change', render); });
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
  window.SurfaceQuote = { add: addPanels, rows: function () { return rows; } };   // for testing
})();
