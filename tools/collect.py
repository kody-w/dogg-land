#!/usr/bin/env python3
"""A federated tick-network node: this repo's own append-only chain, keyed to the
global tick spine at kody-w/dogg.

THEME = "land": a TEMPLATE deed record. This node does not (and cannot) attest to
real title — it demonstrates the SHAPE a land-integrity frame would carry: a document
hash, a pointer to the county-recorder record that is the actual legal source of
truth, and a corner-coordinate polygon. Every field here is a PLACEHOLDER over one
public landmark polygon (the Georgia State Capitol block, Atlanta — approximate,
illustrative only, not a survey). Swap the placeholders for a real document hash and
a real registry pointer to make this carry an actual parcel; until then it proves the
chain mechanics, not any claim about land.

Every run reads the spine's current tick anchor, takes this node's themed snapshot,
and appends one frame referencing that tick. Different repos, run by different
people, each with their own outlook — all joinable on the tick key. To start your own
node: fork this repo, edit THEME/STREAM/SOURCES below, enable the scheduled workflow.
Frames verify with the reference implementation (tools/rapp.py, from kody-w/rapp-1);
CI re-verifies the whole chain on every push.
"""
import json, sys, pathlib, datetime, math, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import rapp as R
import chainio

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPINE_HEAD = "https://raw.githubusercontent.com/kody-w/dogg/main/ticks/HEAD.json"
TIMEOUT = 8

# ---- edit these three for your node -------------------------------------------------
THEME = "land"                        # also the data directory name
STREAM = "land:@kody-w/dogg-land"                          # your stream id (your repo, your name)
# SOURCES: name -> zero-arg callable returning a SMALL dict of facts.
# rapp/1 canonical hashing forbids floats: numeric facts ride as strings or ints.
# -------------------------------------------------------------------------------------

def utc():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"tick-node-{THEME}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

# The sample parcel: an approximate polygon over the Georgia State Capitol block,
# Atlanta, GA — a PUBLIC landmark, chosen only because its rough footprint is public
# knowledge. Corners are illustrative (hand-picked to bound the block), not surveyed.
_SAMPLE_CORNERS = [
    (33.7502, -84.3908),   # NW
    (33.7502, -84.3874),   # NE
    (33.7478, -84.3874),   # SE
    (33.7478, -84.3908),   # SW
]

def _shoelace_m2(corners):
    """Planar shoelace area in m^2, via an equirectangular projection centered on the
    polygon's mean latitude. Good enough for a small city-block-scale polygon; not a
    geodesic survey calculation."""
    R_EARTH = 6371000.0
    lat0 = sum(c[0] for c in corners) / len(corners)
    def to_xy(lat, lon):
        x = math.radians(lon) * R_EARTH * math.cos(math.radians(lat0))
        y = math.radians(lat) * R_EARTH
        return x, y
    pts = [to_xy(lat, lon) for lat, lon in corners]
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return int(round(abs(area) / 2.0))

def _land_snapshot(record_version):
    corners = [[f"{lat:.4f}", f"{lon:.4f}"] for lat, lon in _SAMPLE_CORNERS]
    return {
        "parcel": {
            "document_sha256": "PLACEHOLDER",
            "registry_pointer": "PLACEHOLDER (county recorder URL)",
            "corners": corners,
            "landmark": "Georgia State Capitol block, Atlanta, GA (public landmark "
                        "example — approximate footprint, not a survey)",
        },
        "corner_count": len(corners),
        "area_m2": _shoelace_m2(_SAMPLE_CORNERS),
        "record_version": record_version,
    }

def load_chain(d):
    return chainio.load_chain(d)

def main():
    spine = get(SPINE_HEAD)
    tick_n, tick_hash = spine["count"] - 1, spine["head_frame"]
    d = ROOT / THEME
    d.mkdir(exist_ok=True)
    chain = load_chain(d)
    head = chain[-1] if chain else None
    if head is not None and head["payload"].get("tick") == tick_n:
        print(f"{THEME}: tick {tick_n} already recorded — nothing to do")
        return
    record_version = (head["payload"][THEME]["deed"]["record_version"] + 1) if head else 1
    # SOURCES: name -> zero-arg callable returning a SMALL dict of facts.
    # rapp/1 canonical hashing forbids floats: numeric facts ride as strings or ints.
    SOURCES = {"deed": lambda: _land_snapshot(record_version)}
    data, failed = {}, []
    for name, fn in SOURCES.items():
        try:
            data[name] = fn()
        except Exception:
            failed.append(name)
    payload = {"tick": tick_n, "tick_frame": tick_hash, "spine": "kody-w/dogg",
               "fetched_utc": utc(), THEME: data, "sources_failed": failed}
    if head is None:
        payload["about"] = (f"A federated node of the global tick network: this "
                            f"repo's own {THEME} outlook, one frame per observed "
                            "tick, keyed to the spine's tick anchors so it joins "
                            "every other node's data on the same clock. THEME=land "
                            "carries a TEMPLATE deed record over a public landmark "
                            "polygon — placeholders, not a real title claim.")
    f = R.build_frame(f"{THEME}.snapshot", STREAM, (head["seq"] + 1) if head else 0,
                      utc(), payload, prev=(head["payload_hash"] if head else None))
    ok, step, why = R.verify_frame(f, head=head, stream_id_of_record=STREAM)
    if not ok:
        raise ValueError(f"refusing invalid frame: {step}: {why}")
    chainio.append_frame(d, f, STREAM)
    print(f"{THEME} frame {f['seq']} @ spine tick {tick_n}: {', '.join(data) or 'nothing'}"
          + (f" (failed: {', '.join(failed)})" if failed else ""))

if __name__ == "__main__":
    main()
