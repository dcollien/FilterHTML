# Backlog

Findings from the security review (2026-10-29). Highest priority first.

**0.7.0 parser rewrite (branch `security-review`) fixes #1–7, #9, #10, #12, #13.**
Still open: #8, #11, and the follow-ups at the bottom.

## P0 — XSS

1. **Named entities bypass the `url` rule (Py + JS).**
   `<a href="javascript&colon;alert&lpar;1&rpar;">` passes unchanged; the browser
   decodes it to `javascript:alert(1)`. Only `&#` is blocked. Same trick works in
   `style` values with loose rules (`&semi;`, `&colon;`).
2. **`'script': False` outputs script contents raw (Py only).**
   `<script><img src=x onerror=alert(1)></script>` → `<img src=x onerror=alert(1)>`.
   `script` is in the spec, so it is never added to the default removals.
3. **`remove=[...]` without `'script'` outputs script contents raw (Py + JS).**
   Passing `remove=['style']` or `remove=[]` replaces the default list, so
   non-whitelisted script contents pass through unescaped.

## P1 — Crashes (user-triggerable)

4. **Py: `&#` in a list-rule or style attribute raises `TypeError`.**
   `rules in INVALID_ATTRIBUTE_REPLACEMENTS` with an unhashable list/dict.
   e.g. `target="&#95;blank"`, `style="&#99;olor:red"`.
5. **JS: `True` used instead of `true`.** Every `"boolean"` attribute without `=`
   and every `"text"` rule throws `ReferenceError`.
6. **JS: spec lookups hit `Object.prototype`.** e.g. `<constructor link="x">`
   throws. Use `hasOwnProperty`.

## P2 — Incorrect filtering

7. **`False` tags don't remove their contents.** Py still outputs whitelisted tags
   inside (`<iframe><b>` → `<b></b>`); JS keeps text too (`get_tag_spec` turns
   `false` into `null`).
8. **A single-string rule is a substring check.** `'target': '_blank'` accepts
   `_b` and `""`.
9. **JS: `HTML_ESCAPE_QUOTES` has `"` twice**, so `'` is never escaped.
10. **Py: `'^$'` loop overwrites `value` with the rule** (`regex, value = pair`).
11. **Class-list function rules broken.** Py passes the whole class string, not
    the candidate; JS checks `typeof rules` instead of the item, so it never runs.

## P3 — Robustness

12. **Parser state is not reset between `filter()` calls.** A reused `HTMLFilter`
    left in `script-data`/`skip-data` swallows the next input. Also Py
    `self.tag_removing == None` is a compare, not an assignment.
13. **A lone `<` in text deletes everything up to the next `>`.**
    `1 < 2 and 3 > 2` loses text.

## Follow-ups (raised during design, not yet decided)

14. **CSS escapes beyond hex.** `exp\ression` → `expression`. Only `\` + hex is
    blocked; loose style rules can still be fooled. Option: reject any `\` in styles.
15. **Tabs/newlines in URLs.** Browsers drop them, so `/<tab>/evil.com` slips past
    the `//` check (open redirect, not XSS).
16. **Readme warning** that `"*"` rules on `on*`, `srcdoc`, `style`, `href` are
    unsafe however well encoded.
17. **Shared test cases** for Python and JS, so the two can't drift apart again.
18. **Allowed `<script>` content in Python** is cut at the first `</script>`, without
    the browser's `<!--<script>` rule. Only matters when the spec allows scripts.
