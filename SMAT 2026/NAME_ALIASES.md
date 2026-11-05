# SMAT 2026 Player Name Aliases

Source: `CFC Fantasy League Live SMAT Test2 2025.json`  
Compiled: 2026-11-05

## Confirmed alias groups (20)

| # | Team | Names (season points / roster-only) | Notes |
|---:|---|---|---|
| 1 | Baroda | `Rasikh Salam Dar` (226), `Rasikh Salam` (60), `Rasikh Dar Salam` (7) | Current `Rasikh` + `Salam` rule resolves these. |
| 2 | Baroda | `Ninad Ashvinkumar Rathva` (320), `Ninad Rathva` (10) | Short-name alias. |
| 3 | Baroda | `Atit Sheth` (481), `A Sheth` (50) | Initial-based alias. |
| 4 | Delhi | `Digvesh Singh Rathi` (286), `Digvesh Rathi` (115), `Digvesh` (CFC roster) | `Digvesh` rule resolves; CFC roster updated to `Digvesh Rathi`. |
| 5 | Delhi | `Ishant Sharma` (109), `Ishant` (20) | Delhi player only; `Ishant Bhardwaj` is Haryana and is not this group. |
| 6 | Hyderabad | `Mohammad Arfaz Ahmed` (409), `Arfaz Ahmed Mohammad` (79) | Reversed token order; explicit rule added. |
| 7 | Uttarakhand | `Jagadeesha Suchith` (42), `J Suchith` (495) | Initial token mismatch; explicit rule added. |
| 8 | Tripura | `Manisankar Murasingh` (1020), `M Murasingh` (-3) | Initial-based alias. |
| 9 | Tamil Nadu | `Narayan Jagadeesan` (424), `N Jagadeesan` (38) | Initial-based alias. |
| 10 | Tamil Nadu | `Ravisrinivasan Sai Kishore` (2), `Sai Kishore` (207) | Duplicate removed from squad; `Sai Kishore` kept as canonical. |
| 11 | Bihar | `Sakibul Gani` (117), `S Gani` (438) | Initial token mismatch; explicit rule added. |
| 12 | Mumbai | `Siddhesh Lad` (-15), `S Lad` (25) | Initial token mismatch; explicit rule added. |
| 13 | Saurashtra | `Dharmendrasinh Jadeja` (-15), `DA Jadeja` (203) | Initial token mismatch; explicit rule added. |
| 14 | Andhra | `Cheepurapalli Stephen` (87), `C Stephen` (52) | Initial token mismatch; explicit rule added. |
| 15 | Andhra | `SDNV Prasad` (207), `Singupuram Prasad` (120) | Canonical squad name and scorecard name disagree. |
| 16 | Railways | `Mohammad Saif` (66), `M Saif` (85) | Initial token mismatch; explicit rule added. |
| 17 | Himachal Pradesh | `Aryaman Singh Dhaliwal` (215), `Aryaman Singh` (-9) | Short-name alias. |
| 18 | Tamil Nadu | `R Rajkumar` (457), `Rajkumar Ravichandran` (squad), `Rajkumar Ravichandiran` (CFC roster) | Explicit rule added; CFC roster updated to `Rajkumar Ravichandran`. |
| 19 | Hyderabad | `Aman Rao Perala` (703), `Aman Akram Rao` (CFC roster) | Explicit rule added; CFC roster updated to `Aman Rao Perala`. |
| 20 | Andhra | `Srikar Bharat` (649), `K S Bharat` (CFC roster) | Explicit rule added; CFC roster updated to `Srikar Bharat`. |

## Legacy shared-name keys in pre-change output (3)

These are single JSON keys containing two different real players in the old output. Current squads already split `Sunil Kumar` / `Prince Yadav`, and Delhi `Ankit Kumar` has been renamed `Ankit Rajesh Kumar`; no exact shared squad names remain after a rescrape.

| Key | Teams sharing the key | Season points |
|---|---|---:|
| `Sunil Kumar` | UP and J&K | 397 |
| `Prince Yadav` | UP and Delhi | 617 |
| `Ankit Kumar` | Delhi and Haryana | 1077 |

## Same-name disambiguation

- Delhi `Ankit Kumar` is now `Ankit Rajesh Kumar`; Haryana keeps `Ankit Kumar`. Disruptors owns Haryana `Ankit Kumar`.

## Resolution status

Alias rules for groups 1-20 and the CFC roster names were updated in `Scraping.py` / `Auction.py`. Existing frozen JSON still contains old keys until a forced rescrape.

## Related name issues

- `Devdutt PadikkalManvanth Kumar L` (887) is a merged key, not one player. The missing comma is fixed at `Auction.py:563-564`; the JSON still needs regeneration.
- `Nitish Reddy` was merged into `Nitish Kumar Reddy` (509); the separate `Nitish Reddy` key no longer exists.
