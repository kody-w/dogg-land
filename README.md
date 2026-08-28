# dogg-land — a federated node of the global tick network

**A TEMPLATE deed record, per tick: a document hash, a county-recorder pointer, and a
corner-coordinate polygon — over one public landmark, with every real-world value left
as an explicit placeholder.**

This repo keeps its own append-only chain of rapp/1 frames in `land/`. Once a day a
GitHub Action reads the current tick anchor from the spine at
[kody-w/dogg](https://github.com/kody-w/dogg) and appends one frame of this node's
outlook, referencing that tick — so this chain joins every other node's data on the
same clock. "Right now" APIs only serve the present; the network keeps every present.

## What this node carries

Each frame's `payload.land.deed` is:

- `parcel.document_sha256` — **`"PLACEHOLDER"`**. In a real deployment this is the
  sha256 of an actual recorded deed document.
- `parcel.registry_pointer` — **`"PLACEHOLDER (county recorder URL)"`**. In a real
  deployment this is a URL into the county recorder's public index for the instrument.
- `parcel.corners` — an ordered ring of `[lat, lon]` strings. The sample polygon is an
  **approximate** footprint of the Georgia State Capitol block in Atlanta, GA — a
  public landmark, chosen only because its rough shape is public knowledge and hand-
  picked to bound the block, **not surveyed**.
- `corner_count`, `area_m2` — a shoelace-formula area (equirectangular projection
  centered on the polygon's mean latitude) over the sample polygon, and its vertex
  count.
- `record_version` — increments once per frame, standing in for a real deed's
  amendment/re-recording counter.

## Why this matters offline / for heirlooms

A deed is a claim about the physical world that a family needs to be able to prove
was made, and when, independent of any single institution's uptime — a county
website, a title company, a cloud database. This node's *mechanism* is the point: an
append-only, independently-verifiable chain that a descendant (or an agent acting for
one) can re-check byte-for-byte decades later, with no server trust required, as long
as they have `tools/rapp.py` and the frames. Point `parcel.document_sha256` at a real
document's hash and `parcel.registry_pointer` at the real recorder entry, and the same
mechanism carries an actual family record instead of a template.

## Precision and limits — read before trusting anything here

- **This chain proves integrity, not title.** It proves that a given set of bytes
  (a document hash, a set of corners, a version number) was recorded at a given tick
  and has not been altered since. It does **not** verify that the underlying deed is
  valid, unencumbered, or even real — legal accuracy of the land record is the
  owner's duty, checked against the actual county recorder, always.
- **The sample polygon is illustrative, not a survey.** The corners are hand-picked
  to approximate a public landmark's block; they are not derived from a plat, GPS
  survey, or any authoritative boundary source.
- **`area_m2` is a planar approximation.** Fine at city-block scale; do not use this
  method for anything requiring geodesic precision.
- **Every "real" field is a placeholder until you replace it.** `document_sha256` and
  `registry_pointer` read `"PLACEHOLDER"` / `"PLACEHOLDER (county recorder URL)"` on
  purpose — this repo ships with no real personal or property data in it anywhere.

**Verify it yourself:** `python3 tools/verify_thread.py` re-checks every frame with the
reference implementation from [kody-w/rapp-1](https://github.com/kody-w/rapp-1). CI runs
the same oracle on every push.

**Start your own node:** fork this repo, edit `THEME` / `STREAM` / `SOURCES` at the top
of `tools/collect.py` (keyless https APIs, small factual payloads, numbers as strings),
and enable the scheduled workflow. Your chain, your outlook, same clock — announce it on
the spine's registry ([kody-w/dogg](https://github.com/kody-w/dogg) issues) so agents
can find it.

## Trust

<!--trust-->
No ratings yet — used this chain? [Rate it](../../issues/new?template=rate.yml): valid ratings publish automatically as verifiable frames.
<!--/trust-->

## Summon this node

A MISSION chant — 14 words — carries the `land:@kody-w/dogg-land` dimension's identity, its tick, a hash prefix that pins the exact frame, and a quantized snapshot of corner_count, area_m2, record_version.

```
KNELL CAST PURE GLEAM FORGE BLUFF BATCH ANVIL PANACEA BOND DENSE GRAND GLEAM FLOOD
```

`dogg:1:14:BIALTtAAAcGaQB1B-FKTNAAw`

Tap to decode: [https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALTtAAAcGaQB1B-FKTNAAw](https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALTtAAAcGaQB1B-FKTNAAw)

This chant carries three things: which dimension it names (`land:@kody-w/dogg-land`), which tick and frame it was cut from (tick 1, hash prefix `30669`), and the field values above, quantized (log-quantized, ~0.3% relative (1e-6 … 1e15)) — enough to recognize the node and sanity-check a claim about it without touching the network.

This is a snapshot of one tick (tick 1) — the numbers move as the stream advances, so re-mint with `python3 tools/dogg.py mission land:@kody-w/dogg-land` for the latest.
