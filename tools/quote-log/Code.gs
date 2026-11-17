/**
 * Surface Studio quote log: Google Apps Script web app.
 *
 * The website's instant quote posts each quote here:
 *   - event "calculated": a visitor worked out a price (saved once per quote code)
 *   - event "whatsapp":   the visitor asked for the breakdown on WhatsApp (with name + mobile)
 * Rows go into two tabs of the spreadsheet this script is attached to:
 *   Quotes  one row per event, newest at the bottom
 *   Panels  every panel of each quote code, with its sq ft, rft and amount (the breakdown)
 *
 * Setup: open the Google Sheet → Extensions → Apps Script → paste this file → Deploy →
 * New deployment → Web app → Execute as: Me, Who has access: Anyone → copy the /exec URL.
 */

var QUOTE_HEADERS = ['Time (IST)', 'Event', 'Quote code', 'Name', 'Mobile', 'Finish', 'Panels', 'Sq ft', 'Rft',
  'Design pcs', 'Rate / sq ft', 'Rate / rft', 'Subtotal', 'GST', 'Total', 'Cutlist file', 'Drawings', 'Page', 'Follow-up notes'];
var PANEL_HEADERS = ['Quote code', '#', 'Part', 'Length mm', 'Width mm', 'Qty', 'Sides', 'Edges', 'Design',
  'Sq ft', 'Rft', 'Amount'];
var MAX_BODY = 100000, MAX_ROWS = 400;

function doPost(e) {
  try {
    var body = (e && e.postData && e.postData.contents) || '';
    if (!body || body.length > MAX_BODY) return out_({ ok: false, error: 'bad size' });
    var d = JSON.parse(body);
    if (d.v !== 1 || ['calculated', 'whatsapp'].indexOf(d.event) < 0) return out_({ ok: false, error: 'bad event' });
    if (!/^SSQ-\d{6}-[A-Z0-9]{6}$/.test(String(d.code || ''))) return out_({ ok: false, error: 'bad code' });

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var quotes = sheet_(ss, 'Quotes', QUOTE_HEADERS);
      var panels = sheet_(ss, 'Panels', PANEL_HEADERS);

      // Save a "calculated" quote only once per code.
      if (d.event === 'calculated' && codeExists_(quotes, d.code)) return out_({ ok: true, duplicate: true });

      var time = Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyy-MM-dd HH:mm:ss');
      quotes.appendRow([time, d.event, d.code, clean_(d.name, 80), cleanPhone_(d.phone), clean_(d.finish, 80),
        num_(d.panels), num_(d.sqft), num_(d.rft), num_(d.designPcs), num_(d.rateSqft), num_(d.rateRft),
        num_(d.subtotal), num_(d.gst), num_(d.total), clean_(d.source, 80), num_(d.drawings), clean_(d.page, 80), '']);

      // Store the panel breakdown once per quote code.
      if (Array.isArray(d.rows) && d.rows.length && !codeExists_(panels, d.code)) {
        var out = d.rows.slice(0, MAX_ROWS).map(function (r, i) {
          return [d.code, i + 1, clean_(r[0], 60), num_(r[1]), num_(r[2]), num_(r[3]), num_(r[4]),
            clean_(r[5], 1), clean_(r[6], 1), num_(r[7]), num_(r[8]), num_(r[9])];
        });
        panels.getRange(panels.getLastRow() + 1, 1, out.length, PANEL_HEADERS.length).setValues(out);
      }
    } finally {
      lock.releaseLock();
    }
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, error: 'server error' });
  }
}

function doGet() {
  return out_({ ok: true, service: 'Surface Studio quote log' });
}

/* ---------- helpers ---------- */
function sheet_(ss, name, headers) {
  var sh = ss.getSheetByName(name) || ss.insertSheet(name);
  if (sh.getLastRow() === 0) {
    sh.appendRow(headers);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  }
  return sh;
}
function codeExists_(sh, code) {
  var col = sh.getName() === 'Quotes' ? 3 : 1;
  if (sh.getLastRow() < 2) return false;
  return !!sh.getRange(2, col, sh.getLastRow() - 1, 1).createTextFinder(code).matchEntireCell(true).findNext();
}
// Text is stored as plain values. A leading = + - @ is escaped so a visitor cannot inject a spreadsheet formula.
function clean_(v, max) {
  var s = String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}
function cleanPhone_(v) {
  var s = String(v == null ? '' : v).replace(/[^0-9+()\-\s]/g, '').trim().slice(0, 20);
  return s ? "'" + s : '';
}
function num_(v) {
  var n = Number(v);
  return isFinite(n) ? n : '';
}
function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
