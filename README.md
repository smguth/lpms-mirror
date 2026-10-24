# LPMS mirror

Verbatim copies of the U.S. Army Corps of Engineers LPMS feeds
(lock delays, stoppages, and per-lock queues for the Chicago -> Mobile
Great Loop chain), refreshed every ~15 minutes by GitHub Actions onto
the `data` branch.

Why: LPMS (ndc.ops.usace.army.mil) sends no
`Access-Control-Allow-Origin` header, so web pages cannot read it
directly. `raw.githubusercontent.com` serves these files with
`Access-Control-Allow-Origin: *`. Public data, mirrored as-is.
