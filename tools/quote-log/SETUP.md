# Quote log: every website quote saved to Google Sheets

## What it does
- A visitor works out a price in the instant quote. They see **only the total** (incl. GST) and a quote code such as `SSQ-261117-MS2MA4`.
- To get the breakdown they enter **name + mobile** and tap "Get the full breakdown on WhatsApp". WhatsApp opens with their quote code, name, mobile, finish, panel count and total.
- Each quote is saved to the Google Sheet **Surface Studio – Website Quotes** (in surfacestudiohyd@gmail.com's Drive):
  - **Quotes** tab: one row per event. `calculated` = someone priced a job (saved once per quote code, after the numbers stop changing for 5 seconds). `whatsapp` = they asked for the breakdown, with name and mobile. Columns include finish, panels, sq ft, rft, design pieces, rates, subtotal, GST, total, cutlist file name and a "Follow-up notes" column for you.
  - **Panels** tab: every panel of each quote code with sq ft, rft and amount. This is the breakdown you send back.
- When a WhatsApp message arrives, search the sheet for its quote code (Ctrl+F). Both tabs have the full details. File → Download → Microsoft Excel gives an .xlsx copy at any time.

## Switch it on (about 5 minutes)
1. Open the sheet: https://docs.google.com/spreadsheets/d/1SgvSuF3G2-oyFKuCGFxNm9b6x0ScbOZfe__ADn3pxOk/edit
2. **Extensions → Apps Script.** Delete the sample code, paste all of `Code.gs`, and click Save.
3. **Deploy → New deployment →** gear icon **→ Web app.**
   - Description: `Website quote log`
   - Execute as: **Me (surfacestudiohyd@gmail.com)**
   - Who has access: **Anyone** (the website's visitors are not signed in)
4. Click **Deploy**, then **Authorize access**, and allow it to edit your spreadsheets. It only touches the sheet it is attached to.
5. Copy the **Web app URL** (ends in `/exec`) and send it to Claude. It goes into `build/rates.json` as `quote_log_endpoint`, the site is rebuilt, and the security policy then allows `script.google.com` for that purpose only.

Until the URL is set, the calculator works the same but nothing is saved.

## Notes
- **Privacy:** the calculator tells visitors that quotes and the name/mobile they send are kept for follow-up. Panel lists are still read on their device; only the totals and the panel sizes are saved.
- **Spam:** the web app is public. It accepts only well-formed quote codes, caps size at 100 KB and 400 panels, saves each calculated quote once, and escapes text starting with `= + - @` so nobody can inject spreadsheet formulas. If junk rows appear, redeploy with a new URL.
- **Changing the script:** edit `Code.gs`, then Deploy → Manage deployments → Edit → New version. The URL stays the same.
- **Rates are still in the page source.** Hiding the breakdown on screen does not hide the rate card from someone who reads the JavaScript, and the public "PU price per sq ft" page lists the full rate card.
