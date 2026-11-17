// Junction sketch ("Skizze der Kreuzung"): plan view in metres, north up, in the style of a technical drawing.
// Each arm is drawn to scale from its Soll cross section (export: legs[].elements, left to right looking away from
// the junction); the junction area follows the Soll type (roundabout, protected signal, priority, continuous footway,
// cycle crossing). Schematic: arm axes meet in one point, kerb radii and marking positions are drawing values only,
// not design values, and the side of asymmetric elements (one-sided parking or two-way track) is not known.
import { zoomButton } from "./panel.js";
import { esc, num } from "./util.js";

// Drawing values (metres), not rules: they place kerbs and markings so the sketch reads like a plan.
const D = {
  arm: 28, // visible arm length beyond the junction area
  kerbRadius: 6, protectedRadius: 10, protectedCycleRadius: 2, // corner radii of the road edge and cycle track
  zebra: 3, stopGap: 1.5, crossingGap: 1,
  ring: { single: { outer: 13, width: 6 }, turbo: { outer: 19, width: 9 }, apron: 1.5, verge: 5, cycle: 2.5, walk: 2.5 },
  splitter: { length: 10, width: 2.5 },
  pathWidth: 3, // separate cycle path without cross section
  fallback: { sidewalk: 2.5, lane: 3.25, track: 2 }, // arm without Soll cross section
};
const FALLBACK_COLOUR = {
  sidewalk: "#d9d4c7", cycle_track: "#c0392b", cycle_lane: "#e06c5a", buffer_cycle_carriageway: "#9aa39a",
  buffer_to_parking: "#b8beb8", tree_strip: "#5b8c3a", parking_parallel: "#8e9aaf", loading_zone: "#c9a227",
  bus_lane: "#b03a8c", carriageway: "#555b61", median: "#7da35a", shared_surface: "#a39a8a", tram: "#6b5b95",
};
const PED = new Set(["sidewalk"]);
const CYC = new Set(["cycle_track"]);
const ROAD = new Set(["cycle_lane", "buffer_to_parking", "bus_lane", "carriageway", "median", "shared_surface", "tram"]);
const CAT_RANK = { SW: 5, GOW80: 4, GOW50: 4, ETW60: 3, GOW30: 3, ETW30: 2, ETW_ERF: 1 };
const MARK = "#ffffff";
const LINE = "#1a1a1a";
const SURFACE = "#9c5f4a"; // coloured junction area
const MARKINGS = {
  cycle_priority: "Radfurt, Radverkehr hat Vorrang", cycle_yield: "Radfurt, Radverkehr wartet", zebra: "Fußgängerüberweg",
  stop: "Haltlinie", giveway: "Vorfahrt achten (Haifischzähne)", signal: "Ampel", raised: "erhöhte Fläche (Plateau)",
  coloured: "eingefärbte Kreuzungsfläche", footway: "durchgehender Gehweg (erhöht)", green: "Grünfläche, Insel",
  bridge: "Radweg auf Brücke oder im Tunnel", bike: "Radverkehr auf der Fahrbahn", refuge: "Mittelinsel",
};

const rad = (b) => (b * Math.PI) / 180;
const f = (v) => (Math.abs(v) < 5e-4 ? "0" : v.toFixed(2).replace(/\.?0+$/, ""));
const P = ([x, y]) => `${f(x)} ${f(y)}`;

/** Arm frame: u points away from the junction, r to the right of u (SVG y points down, north = up). */
function frame(b) {
  const u = [Math.sin(rad(b)), -Math.cos(rad(b))];
  return { u, r: [-u[1], u[0]] };
}
const at = (a, d, s) => [a.u[0] * d + a.r[0] * s, a.u[1] * d + a.r[1] * s];

function fallbackElements(leg) {
  const fb = D.fallback;
  const lanes = (leg.lanes || 1) * (leg.oneway ? 1 : 2);
  const track = ["separated_oneway_both", "separated_twoway"].includes(leg.facility) ? [["cycle_track", fb.track]] : [];
  return [["sidewalk", fb.sidewalk], ...track, ["carriageway", lanes * fb.lane], ...track.slice().reverse(), ["sidewalk", fb.sidewalk]];
}

/** Distances from the axis of the zone boundaries on one side: out (property line), ped (inner sidewalk edge),
 * cyc (inner cycle track edge), road (edge of the carriageway incl. bus and cycle lanes). */
function zones(els, W) {
  const side = (list) => {
    let x = 0, ped = 0, cyc = 0, road = null;
    for (const [e, w] of list) {
      if (ROAD.has(e)) { road = x; break; }
      x += w;
      if (PED.has(e)) ped = x;
      if (CYC.has(e)) cyc = x;
    }
    road ??= W / 2;
    cyc = Math.max(cyc, ped);
    road = Math.max(road, cyc);
    return { out: W / 2, ped: W / 2 - ped, cyc: W / 2 - cyc, road: W / 2 - road };
  };
  return { L: side(els), R: side([...els].reverse()) };
}

function arms(legs) {
  const known = legs.every((l) => l.bearing != null);
  return legs.map((l, i) => {
    const path = l.cat === "cycle_path";
    const est = !path && !l.elements?.length;
    const els = path ? [["cycle_track", D.pathWidth]] : est ? fallbackElements(l) : l.elements;
    const W = els.reduce((a, [, w]) => a + w, 0);
    const b = known ? l.bearing : (360 / legs.length) * i;
    return { ...l, b, path, est, els, W, ...frame(b), ...zones(els, W) };
  }).sort((a, b) => a.b - b.b);
}

const roadW = (a) => a.L.road + a.R.road;
const rank = (a) => (a.facility === "cycle_street" ? 10 : 0) + (CAT_RANK[a.cat] ?? 0) + (a.lanes || 1) / 10;

/** Corner between arm A and the next arm B clockwise, for one zone boundary k: right edge of A meets left edge of B,
 * rounded with radius R (quadratic curve). Wide corners (≥ 175°) are bridged around the back of the junction. */
function corner(A, B, k, R) {
  const hA = A.R[k], hB = B.L[k];
  const g = ((B.b - A.b) + 360) % 360 || 360;
  if (g >= 175) {
    const pA = at(A, 0, hA), pB = at(B, 0, -hB);
    const bis = frame(A.b + g / 2).u, m = Math.max(hA, hB) / Math.max(Math.sin(rad(g / 2)), 0.5);
    return { tA: 0, tB: 0, FA: pA, P: [bis[0] * m, bis[1] * m], FB: pB };
  }
  // A.r*hA + A.u*t = -B.r*hB + B.u*t'
  const rx = -B.r[0] * hB - A.r[0] * hA, ry = -B.r[1] * hB - A.r[1] * hA;
  const det = A.u[0] * -B.u[1] + B.u[0] * A.u[1];
  const t = (rx * -B.u[1] + B.u[0] * ry) / det;
  const t2 = (A.u[0] * ry - A.u[1] * rx) / det;
  const fl = Math.min(R / Math.tan(rad(g) / 2), 25);
  const tA = t + fl, tB = t2 + fl;
  return { tA, tB, FA: at(A, tA, hA), P: at(A, t, hA), FB: at(B, tB, -hB) };
}

/** Corners of all boundaries; d0 per arm = where the arm leaves the junction area. */
function cornerSet(st, radius) {
  const keys = ["out", "ped", "cyc", "road"];
  const out = {};
  for (const k of keys) {
    out[k] = st.map((A, i) => {
      const B = st[(i + 1) % st.length];
      const dA = A.R[k] - A.R.road, dB = B.L[k] - B.L.road;
      return corner(A, B, k, Math.max(radius(k) - (dA + dB) / 2, 0.5));
    });
  }
  return out;
}

function polygon(st, cs, k, d0) {
  let p = "";
  st.forEach((A, i) => {
    const c = cs[k][i];
    p += `${i ? "L" : "M"}${P(at(A, d0[i], -A.L[k]))}L${P(at(A, d0[i], A.R[k]))}L${P(c.FA)}Q${P(c.P)} ${P(c.FB)}`;
  });
  return `${p}Z`;
}

function kerbPath(st, cs, k, d0) {
  return st.map((A, i) => {
    const B = st[(i + 1) % st.length], j = (i + 1) % st.length, c = cs[k][i];
    return `M${P(at(A, d0[i], A.R[k]))}L${P(c.FA)}Q${P(c.P)} ${P(c.FB)}L${P(at(B, d0[j], -B.L[k]))}`;
  }).join("");
}

/** Junction area of the road: corner curves joined straight across each arm mouth. */
function corePath(st, cs) {
  return `${cs.road.map((c, i) => `${i ? "L" : "M"}${P(c.FA)}Q${P(c.P)} ${P(c.FB)}`).join("")}Z`;
}

const quad = (a, d1, d2, s1, s2) => `M${P(at(a, d1, s1))}L${P(at(a, d2, s1))}L${P(at(a, d2, s2))}L${P(at(a, d1, s2))}Z`;

export function junctionSvg(j, meta, { title: name = "Skizze der Kreuzung" } = {}) {
  const legs = j?.legs ?? [];
  if (!legs.length) return "";
  const colour = (e) => meta?.cycling?.elements?.[e]?.color ?? FALLBACK_COLOUR[e] ?? "#cccccc";
  const label = (e) => meta?.cycling?.elements?.[e]?.label ?? e;
  const all = arms(legs);
  const st = all.filter((a) => !a.path);
  const paths = all.filter((a) => a.path);
  const known = legs.every((l) => l.bearing != null);
  const code = j.soll?.code ?? "";
  const group = j.soll?.group ?? "none";
  const roundabout = group === "roundabout" && st.length > 0;
  const uid = Math.random().toString(36).slice(2, 8);
  const used = new Set(), marks = new Set();
  const g = []; // drawing, bottom to top
  const anyTrack = st.some((a) => a.els.some(([e]) => CYC.has(e)));
  const cw = Math.max(...st.flatMap((a) => a.els.filter(([e]) => CYC.has(e)).map(([, w]) => w)), D.ring.cycle);
  const fill = (d, c, extra = "") => g.push(`<path d="${d}" fill="${c}"${extra}/>`);
  const stroke = (d, c, w, extra = "") => g.push(`<path d="${d}" fill="none" stroke="${c}" stroke-width="${w}"${extra}/>`);

  // --- markings ---
  const band = (a, d, w, s1, s2, kind) => {
    // cycle crossing across an arm: red band with block markings (priority) or block markings only (yield)
    if (kind === "cycle_priority") fill(quad(a, d - w / 2, d + w / 2, s1, s2), colour("cycle_track"));
    for (const e of [d - w / 2 + 0.25, d + w / 2 - 0.25]) stroke(`M${P(at(a, e, s1))}L${P(at(a, e, s2))}`, MARK, 0.5, ' stroke-dasharray="0.5 0.5"');
    marks.add(kind);
  };
  const zebra = (a, d, s1, s2) => {
    stroke(`M${P(at(a, d, s1))}L${P(at(a, d, s2))}`, MARK, D.zebra, ' stroke-dasharray="0.5 0.5"');
    marks.add("zebra");
  };
  const stopLine = (a, d) => {
    const s2 = a.oneway ? a.R.road : 0;
    stroke(`M${P(at(a, d, -a.L.road))}L${P(at(a, d, s2))}`, MARK, 0.3);
    marks.add("stop");
  };
  const teeth = (a, d, s1, s2, inward = false) => {
    // give way: white triangles pointing towards the driver who has to wait
    const h = inward ? -0.7 : 0.7;
    let p = "";
    for (let s = s1 + 0.2; s + 0.6 <= s2; s += 1) p += `M${P(at(a, d, s))}L${P(at(a, d, s + 0.6))}L${P(at(a, d + h, s + 0.3))}Z`;
    if (p) fill(p, MARK);
    marks.add("giveway");
  };
  const signal = (a, d) => {
    const [x, y] = at(a, d, -a.L.road - 0.9);
    g.push(`<g transform="translate(${f(x)},${f(y)}) rotate(${f(a.b)})"><rect x="-0.4" y="-0.9" width="0.8" height="1.8" fill="${LINE}"/>`
      + `<circle cy="-0.5" r="0.22" fill="#CC3311"/><circle r="0.22" fill="#f0c000"/><circle cy="0.5" r="0.22" fill="#117733"/></g>`);
    marks.add("signal");
  };
  const bike = (a, d, s) => {
    const [x, y] = at(a, d, s);
    g.push(`<g transform="translate(${f(x)},${f(y)}) rotate(${f(a.b - 90)})" fill="none" stroke="${MARK}" stroke-width="0.14">`
      + `<circle cx="-0.75" r="0.45"/><circle cx="0.75" r="0.45"/><path d="M-0.75 0L-0.2 -0.75L0.45 -0.75L0.75 0M-0.2 -0.75L0.05 0L0.45 -0.75M0.05 0L-0.75 0"/></g>`);
  };

  // --- arms beyond the junction area: one strip per element, to scale ---
  const drawArm = (a, d0, dEnd, setback) => {
    let s = -a.W / 2;
    const lines = [];
    for (const [e, w] of a.els) {
      const late = !a.path && !ROAD.has(e) && !PED.has(e) && !CYC.has(e) && setback > d0; // parking, trees: start later
      if (late) fill(quad(a, d0, setback, s, s + w), colour("sidewalk"));
      fill(quad(a, late ? setback : d0, dEnd, s, s + w), colour(e));
      used.add(e);
      lines.push([s, e]);
      s += w;
    }
    lines.push([s, null]);
    // boundaries: kerbs black where the road meets a raised element, white markings at bus and cycle lanes
    for (let i = 0; i < lines.length; i++) {
      const [x, e] = lines[i], prev = lines[i - 1]?.[1];
      const road1 = prev && ROAD.has(prev), road2 = e && ROAD.has(e);
      const line = `M${P(at(a, d0, x))}L${P(at(a, dEnd, x))}`;
      if (road1 !== road2 || prev === "median" || e === "median") stroke(line, LINE, 0.15);
      else if (road1 && road2 && [prev, e].some((v) => v === "cycle_lane" || v === "bus_lane")) stroke(line, MARK, 0.25);
      else if (!road1 && !road2) stroke(line, LINE, i === 0 || i === lines.length - 1 ? 0.12 : 0.05, i === 0 || i === lines.length - 1 ? ' stroke-dasharray="1.2 0.6"' : "");
    }
    // lane lines on the carriageway(s)
    const cws = [];
    s = -a.W / 2;
    for (const [e, w] of a.els) { if (e === "carriageway") cws.push([s, w]); s += w; }
    const n = a.lanes || 1;
    const dash = ' stroke-dasharray="3 3"';
    const cat30 = a.cat?.startsWith("ETW") || a.facility === "cycle_street";
    if (!cat30) {
      for (const [x, w] of cws) {
        const parts = cws.length === 1 && !a.oneway ? 2 * n : n;
        for (let k = 1; k < parts; k++) {
          const xs = x + (w * k) / parts;
          const centre = cws.length === 1 && !a.oneway && k === n;
          stroke(`M${P(at(a, d0, xs))}L${P(at(a, dEnd, xs))}`, MARK, centre ? 0.15 : 0.12, dash);
        }
      }
    }
    if (!a.path && !anyTrackOn(a) && a.cycle_cat?.code && cws.length) {
      const [x, w] = cws[0];
      bike(a, dEnd - 3, x + w / 4);
      marks.add("bike");
    }
    if (anyTrackOn(a)) {
      s = -a.W / 2;
      for (const [e, w] of a.els) { if (CYC.has(e) || e === "cycle_lane") bike(a, dEnd - 3, s + w / 2); s += w; }
    }
  };
  const anyTrackOn = (a) => a.els.some(([e]) => CYC.has(e) || e === "cycle_lane");

  let d0 = [], extent = 0, crossings = [];
  if (roundabout) {
    const R = code.startsWith("turbo") ? D.ring.turbo : D.ring.single;
    const cyc = !code.startsWith("turbo") || anyTrack;
    const rIn = R.outer + D.ring.verge, rOut = rIn + cw, rWalk = rOut + D.ring.walk;
    d0 = st.map(() => rWalk + 2);
    const dEnd = rWalk + 2 + D.arm;
    // sidewalk disc and arm mouths, cycle ring, verge, ring road, central island
    fill(`M${-rWalk} 0a${rWalk} ${rWalk} 0 1 0 ${2 * rWalk} 0a${rWalk} ${rWalk} 0 1 0 ${-2 * rWalk} 0Z`, colour("sidewalk"));
    for (const [i, a] of st.entries()) fill(quad(a, 0, d0[i], -a.L.out, a.R.out), colour("sidewalk"));
    if (cyc) {
      g.push(`<circle r="${f((rIn + rOut) / 2)}" fill="none" stroke="${colour("cycle_track")}" stroke-width="${f(cw)}"/>`);
      used.add("cycle_track");
      for (const [i, a] of st.entries()) {
        for (const [s1, s2] of [[-a.L.ped, -a.L.cyc], [a.R.cyc, a.R.ped]]) if (s2 - s1 > 0.1) fill(quad(a, (rIn + rOut) / 2, d0[i], s1, s2), colour("cycle_track"));
      }
    }
    g.push(`<circle r="${f(rIn)}" fill="${colour("median")}"/>`);
    marks.add("green");
    for (const [i, a] of st.entries()) fill(quad(a, 0, d0[i], -a.L.road, a.R.road), colour("carriageway"));
    g.push(`<circle r="${f(R.outer - R.width / 2)}" fill="none" stroke="${colour("carriageway")}" stroke-width="${f(R.width)}"/>`);
    if (code.startsWith("turbo")) g.push(`<circle r="${f(R.outer - R.width / 2)}" fill="none" stroke="${MARK}" stroke-width="0.15" stroke-dasharray="3 3"/>`);
    const rIsl = R.outer - R.width;
    g.push(`<circle r="${f(rIsl)}" fill="#8a8f94" stroke="${LINE}" stroke-width="0.15"/>`,
      `<circle r="${f(rIsl - D.ring.apron)}" fill="${colour("median")}" stroke="${LINE}" stroke-width="0.15"/>`);
    for (const a of st) {
      // splitter island, cycle crossing, zebra, give way for cars entering and leaving
      const sw = Math.min(D.splitter.width, roadW(a) / 3);
      if (roadW(a) > 5) fill(quad(a, R.outer - 0.5, R.outer + D.splitter.length, -sw / 2, sw / 2), colour("sidewalk"), ` stroke="${LINE}" stroke-width="0.15"`);
      if (cyc) {
        const kind = code.includes("cycle_priority") ? "cycle_priority" : "cycle_yield";
        band(a, (rIn + rOut) / 2, cw, -a.L.road, a.R.road, kind);
        if (kind === "cycle_priority") { teeth(a, rOut + 0.6, -a.L.road, -sw / 2); teeth(a, rIn - 0.6, sw / 2, a.R.road, true); }
      }
      zebra(a, R.outer + 2.5, -a.L.road, a.R.road);
      teeth(a, R.outer + 0.4, -a.L.road, roadW(a) > 5 ? -sw / 2 : 0);
    }
    for (const [i, a] of st.entries()) drawArm(a, d0[i], dEnd, d0[i]);
    extent = dEnd;
  } else if (st.length) {
    const prot = code === "signal_protected";
    const radius = (k) => (prot ? (k === "road" ? D.protectedRadius : D.protectedCycleRadius) : D.kerbRadius);
    const cs = cornerSet(st, radius);
    const n = st.length;
    const tOn = (k, i) => Math.max(cs[k][i].tA, cs[k][(i - 1 + n) % n].tB);
    // minor arms: all but the two highest ranked (category, cycle street, lanes)
    const majors = new Set([...st].sort((a, b) => rank(b) - rank(a)).slice(0, 2));
    const minor = (a) => !majors.has(a);
    // crossings per arm: cycle crossing set back from the junction, then zebra, then stop line
    crossings = st.map((a, i) => {
      const dx = Math.max(tOn("cyc", i), tOn("road", i) * (prot ? 0.55 : 1), 0) + cw / 2 + D.crossingGap;
      const dz = dx + cw / 2 + D.crossingGap + D.zebra / 2;
      return { dx, dz, dStop: dz + D.zebra / 2 + D.stopGap };
    });
    const withCrossings = (a) => ["signal_protected", "cycle_crossing_signal"].includes(code)
      || (["priority_raised", "priority_flat_coloured", "continuous_footway_exit", "cycle_crossing_priority", "cycle_crossing_refuge"].includes(code) && minor(a));
    d0 = st.map((a, i) => Math.max(...["out", "ped", "cyc", "road"].map((k) => tOn(k, i)), withCrossings(a) ? crossings[i].dStop + 0.5 : 0, 2));
    const dEnd = Math.max(...d0) + D.arm;
    fill(polygon(st, cs, "out", d0), colour("sidewalk"));
    if (anyTrack) fill(polygon(st, cs, "ped", d0), colour("cycle_track"));
    fill(polygon(st, cs, "cyc", d0), colour("sidewalk"));
    fill(polygon(st, cs, "road", d0), colour("carriageway"));
    stroke(kerbPath(st, cs, "out", d0), LINE, 0.12, ' stroke-dasharray="1.2 0.6"');
    if (anyTrack) stroke(kerbPath(st, cs, "ped", d0), LINE, 0.05);
    stroke(kerbPath(st, cs, "cyc", d0), LINE, 0.15);
    stroke(kerbPath(st, cs, "road", d0), LINE, 0.15);
    used.add("sidewalk").add("carriageway");
    if (code === "priority_flat_coloured") { fill(corePath(st, cs), SURFACE); marks.add("coloured"); }
    if (code === "priority_raised" || code === "cycle_crossing_priority") {
      g.push(`<defs><pattern id="hatch-${uid}" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">`
        + `<line y2="1.2" stroke="${MARK}" stroke-width="0.18"/></pattern></defs>`);
      fill(corePath(st, cs), `url(#hatch-${uid})`);
      marks.add("raised");
    }
    const tracks = anyTrack || ["signal_protected", "cycle_crossing_signal", "cycle_crossing_priority"].includes(code);
    for (const [i, a] of st.entries()) {
      const c = crossings[i];
      if (!withCrossings(a)) continue;
      if (code === "continuous_footway_exit") {
        // footway and cycle track run on across the minor arm
        const ws = Math.max(...st.filter((x) => !minor(x)).map((x) => x.L.out - x.L.ped), D.fallback.sidewalk);
        if (anyTrack) fill(quad(a, c.dx - cw / 2, c.dx + cw / 2, -a.L.cyc, a.R.cyc), colour("cycle_track"));
        fill(quad(a, c.dx + cw / 2, c.dx + cw / 2 + ws, -a.L.cyc, a.R.cyc), colour("sidewalk"), ` stroke="${LINE}" stroke-width="0.12"`);
        teeth(a, c.dx + cw / 2 + ws + 0.6, -a.L.road, a.R.road);
        marks.add("footway");
        continue;
      }
      if (tracks && !["cycle_crossing_priority", "cycle_crossing_refuge"].includes(code)) {
        band(a, c.dx, cw, -a.L.cyc, a.R.cyc, code === "cycle_crossing_signal" || prot || anyTrack ? "cycle_priority" : "cycle_yield");
      }
      if (roadW(a) > 0) zebra(a, c.dz, -a.L.road, a.R.road);
      if (prot || code === "cycle_crossing_signal") { stopLine(a, c.dStop); signal(a, c.dStop); }
      else teeth(a, c.dStop - 0.8, -a.L.road, a.oneway ? a.R.road : 0);
    }
    if (code === "cycle_crossing_refuge" && !paths.length) {
      const a = [...st].sort((x, y) => rank(y) - rank(x))[0];
      fill(quad(a, -6, 6, -1.25, 1.25), colour("sidewalk"), ` stroke="${LINE}" stroke-width="0.15"`);
      marks.add("refuge");
    }
    for (const [i, a] of st.entries()) drawArm(a, d0[i], dEnd, withCrossings(a) ? crossings[i].dStop + 2 : d0[i] + 3);
    extent = dEnd;
  }

  // separate cycle paths: under the road, across it at cycle crossings, on a bridge when grade separated
  const pathEnd = Math.max(extent, 24);
  const over = ["cycle_crossing_priority", "cycle_crossing_signal", "cycle_crossing_refuge", "grade_separated_cycle"].includes(code);
  // a path that does not cross ends at the cycle ring of a roundabout or at the corner of the junction area
  const pathFrom = roundabout ? D.ring[code.startsWith("turbo") ? "turbo" : "single"].outer + D.ring.verge + cw / 2
    : st.length ? Math.min(...d0) * 0.8 : 0;
  for (const a of paths) {
    const from = over ? 0 : pathFrom;
    const w = a.W;
    if (code === "cycle_crossing_refuge" && st.length) {
      const m = [...st].sort((x, y) => rank(y) - rank(x))[0];
      fill(quad(m, -4 - w, 4 + w, -1.25, 1.25), colour("sidewalk"), ` stroke="${LINE}" stroke-width="0.15"`);
      marks.add("refuge");
    }
    fill(quad(a, over ? -0.01 : from, pathEnd, -w / 2, w / 2), colour("cycle_track"));
    stroke(quad(a, over ? -0.01 : from, pathEnd, -w / 2, w / 2), LINE, 0.1);
    used.add("cycle_track");
    if (code === "grade_separated_cycle") {
      for (const s of [-w / 2 - 0.3, w / 2 + 0.3]) stroke(`M${P(at(a, 0, s))}L${P(at(a, Math.min(pathEnd, 14), s))}`, LINE, 0.35);
      marks.add("bridge");
    } else if (over && st.length) {
      for (const s of [-w / 2 + 0.25, w / 2 - 0.25]) stroke(`M${P(at(a, 0, s))}L${P(at(a, Math.max(...st.map((x) => x.L.road + x.R.road)) / 2 + 1, s))}`, MARK, 0.5, ' stroke-dasharray="0.5 0.5"');
      marks.add("cycle_priority");
      if (code === "cycle_crossing_priority") for (const x of st) teeth(x, Math.max(w, 4) + 1.5, -x.L.road, x.oneway ? x.R.road : 0);
      if (code === "cycle_crossing_signal") for (const x of st) { stopLine(x, Math.max(w, 4) + 3); signal(x, Math.max(w, 4) + 3); }
    }
    bike(a, pathEnd * 0.7, 0);
  }
  if (group === "none" && !st.length) extent = pathEnd;

  // street names along the axis, dimension line with the total width at each arm end
  const named = new Set();
  const fs = 1.9;
  const ends = [];
  for (const a of all) {
    const dEnd = a.path ? pathEnd : extent;
    ends.push(at(a, dEnd + 4.5, -a.W / 2), at(a, dEnd + 4.5, a.W / 2));
    const rot = ((a.b - 90) % 360 + 360) % 360;
    const flip = rot > 90 && rot < 270 ? rot - 180 : rot;
    if (!a.path) {
      const y = dEnd + 1.2, [x1, y1] = at(a, y, -a.W / 2), [x2, y2] = at(a, y, a.W / 2);
      stroke(`M${f(x1)} ${f(y1)}L${f(x2)} ${f(y2)}`, LINE, 0.08);
      for (const s of [-a.W / 2, a.W / 2]) stroke(`M${P(at(a, y - 0.6, s))}L${P(at(a, y + 0.6, s))}`, LINE, 0.08);
      const [tx, ty] = at(a, y + 1.8, 0);
      g.push(`<text transform="translate(${f(tx)},${f(ty)}) rotate(${f(flip + 90)})" text-anchor="middle" dominant-baseline="middle" font-size="${f(fs * 0.75)}" fill="${LINE}">${esc(num(a.W, 1))} m</text>`);
    }
    if (a.name && !named.has(a.name)) {
      named.add(a.name);
      const roadMid = a.path ? 0 : (-a.L.road + a.R.road) / 2;
      const d1 = a.path ? pathFrom : d0[st.indexOf(a)];
      const [tx, ty] = at(a, d1 + (dEnd - d1) * 0.5, roadMid);
      g.push(`<text transform="translate(${f(tx)},${f(ty)}) rotate(${f(flip)})" text-anchor="middle" dominant-baseline="middle" font-size="${f(fs)}" `
        + `fill="${MARK}" stroke="${LINE}" stroke-width="0.5" paint-order="stroke" font-weight="600">${esc(a.name.length > 26 ? `${a.name.slice(0, 25)}…` : a.name)}</text>`);
    }
  }

  // sheet: drawing area, north arrow, scale bar, legend, title block
  const xs = ends.map((p) => p[0]), ys = ends.map((p) => p[1]);
  const pad = 3;
  let x0 = Math.min(...xs, -extent) - pad, x1 = Math.max(...xs, extent) + pad;
  const y0 = Math.min(...ys, -extent) - pad, y1 = Math.max(...ys, extent) + pad;
  if (x1 - x0 < 70) { const c = (x0 + x1) / 2; x0 = c - 35; x1 = c + 35; }
  const Wd = x1 - x0;
  const u = Wd / 46; // text unit of the sheet
  const legendItems = [...Object.keys(FALLBACK_COLOUR).filter((e) => used.has(e)).map((e) => ({ swatch: colour(e), text: label(e) })),
    ...Object.keys(MARKINGS).filter((m) => marks.has(m)).map((m) => ({ mark: m, text: MARKINGS[m] }))];
  const cols = 2;
  const colW = Wd / cols;
  const rowH = u * 1.7;
  const rows = Math.ceil(legendItems.length / cols);
  const yScale = y1 + u * 1.2;
  const yLegend = yScale + u * 3;
  const yTitle = yLegend + rows * rowH + u * 1.2;
  const notes = [`heute: ${j.ist?.text ?? "unbekannt"}`];
  if (!known) notes.push("Lage der Arme schematisch");
  if (st.some((a) => a.est)) notes.push("Querschnitt einzelner Arme geschätzt");
  const H = yTitle + u * (2.6 + 1.5 * notes.length) - y0;
  const id = `jx-${uid}`;
  const uniq = [...new Set(legs.map((l) => l.name).filter(Boolean))];
  const title = `${name}: ${legs.length} Arme${uniq.length ? ` (${uniq.join(", ")})` : ""}. Heute: ${j.ist?.text ?? "unbekannt"}. `
    + `Ziel: ${j.soll?.text ?? "kein Soll-Typ"}. Draufsicht, Norden oben, Arme im Soll-Querschnitt.${known ? "" : " Lage der Arme schematisch."}`;

  const sheet = [];
  // north arrow
  const nx = x1 - u * 1.6, ny = y0 + u * 2;
  sheet.push(`<g transform="translate(${f(nx)},${f(ny)})"><path d="M0 ${f(-u * 1.3)}L${f(u * 0.5)} ${f(u * 0.6)}L0 ${f(u * 0.2)}L${f(-u * 0.5)} ${f(u * 0.6)}Z" fill="${LINE}"/>`
    + `<text y="${f(u * 1.9)}" text-anchor="middle" font-size="${f(u)}" fill="${LINE}">N</text></g>`);
  // scale bar
  const step = Wd > 140 ? 20 : 10;
  for (let k = 0; k < 2; k++) sheet.push(`<rect x="${f(x0 + pad + k * step)}" y="${f(yScale)}" width="${step}" height="${f(u * 0.5)}" fill="${k ? MARK : LINE}" stroke="${LINE}" stroke-width="0.1"/>`);
  for (let k = 0; k <= 2; k++) sheet.push(`<text x="${f(x0 + pad + k * step)}" y="${f(yScale + u * 1.6)}" text-anchor="middle" font-size="${f(u * 0.8)}" fill="${LINE}">${k * step}${k === 2 ? " m" : ""}</text>`);
  // legend
  legendItems.forEach((it, k) => {
    const cx = x0 + pad + (k % cols) * colW, cy = yLegend + Math.floor(k / cols) * rowH;
    const sw = u * 1.6, sh = u * 1;
    if (it.swatch) sheet.push(`<rect x="${f(cx)}" y="${f(cy)}" width="${f(sw)}" height="${f(sh)}" fill="${it.swatch}" stroke="${LINE}" stroke-width="0.08"/>`);
    else sheet.push(legendMark(it.mark, cx, cy, sw, sh, colour, uid));
    sheet.push(`<text x="${f(cx + sw + u * 0.5)}" y="${f(cy + sh / 2)}" dominant-baseline="middle" font-size="${f(u * 0.8)}" fill="${LINE}">${esc(it.text)}</text>`);
  });
  // title block
  sheet.push(`<line x1="${f(x0)}" y1="${f(yTitle - u * 0.6)}" x2="${f(x1)}" y2="${f(yTitle - u * 0.6)}" stroke="${LINE}" stroke-width="0.1"/>`);
  sheet.push(`<text x="${f(x0 + pad)}" y="${f(yTitle + u)}" font-size="${f(u)}" font-weight="700" fill="${LINE}">Ziel: ${esc(j.soll?.text ?? "kein Soll-Typ")}</text>`);
  notes.forEach((t, k) => sheet.push(`<text x="${f(x0 + pad)}" y="${f(yTitle + u * (2.5 + 1.5 * k))}" font-size="${f(u * 0.85)}" fill="#333333">${esc(t)}</text>`));
  sheet.push(`<text x="${f(x1 - pad)}" y="${f(yTitle + u * 2.5)}" text-anchor="end" font-size="${f(u * 0.7)}" fill="#555555">Arme maßstäblich, Kreuzungsbereich schematisch</text>`);

  return `<figure class="sketch jx">${zoomButton(id)}<svg viewBox="${f(x0)} ${f(y0)} ${f(Wd)} ${f(H)}" role="img" aria-labelledby="${id}" `
    + `font-family="inherit" style="background:#fbfbf8"><title id="${id}">${esc(title)}</title>`
    + `<rect x="${f(x0 + 0.3)}" y="${f(y0 + 0.3)}" width="${f(Wd - 0.6)}" height="${f(H - 0.6)}" fill="none" stroke="${LINE}" stroke-width="0.25"/>`
    + `<g class="plan">${g.join("")}</g>${sheet.join("")}</svg></button></figure>`;
}

function legendMark(m, x, y, w, h, colour, uid) {
  const r = `x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}"`;
  const road = `<rect ${r} fill="${colour("carriageway")}"/>`;
  const mid = y + h / 2;
  switch (m) {
    case "cycle_priority": return `<rect ${r} fill="${colour("cycle_track")}"/><path d="M${f(x)} ${f(y + 0.15)}H${f(x + w)}M${f(x)} ${f(y + h - 0.15)}H${f(x + w)}" stroke="${MARK}" stroke-width="0.3" stroke-dasharray="0.3 0.3"/>`;
    case "cycle_yield": return `${road}<path d="M${f(x)} ${f(y + 0.15)}H${f(x + w)}M${f(x)} ${f(y + h - 0.15)}H${f(x + w)}" stroke="${MARK}" stroke-width="0.3" stroke-dasharray="0.3 0.3"/>`;
    case "zebra": return `${road}<path d="M${f(x)} ${f(mid)}H${f(x + w)}" stroke="${MARK}" stroke-width="${f(h * 0.8)}" stroke-dasharray="0.35 0.35"/>`;
    case "stop": return `${road}<path d="M${f(x + w / 2)} ${f(y)}V${f(y + h)}" stroke="${MARK}" stroke-width="0.3"/>`;
    case "giveway": return `${road}<path d="M${f(x + 0.2)} ${f(y + 0.2)}l0.5 0l-0.25 0.6zM${f(x + 1)} ${f(y + 0.2)}l0.5 0l-0.25 0.6z" fill="${MARK}"/>`;
    case "signal": return `<rect x="${f(x + w / 2 - 0.3)}" y="${f(y)}" width="0.6" height="${f(h)}" fill="${LINE}"/>`;
    case "raised": return `${road}<path d="M${f(x)} ${f(y + h)}L${f(x + h)} ${f(y)}M${f(x + w / 2)} ${f(y + h)}L${f(x + w / 2 + h)} ${f(y)}" stroke="${MARK}" stroke-width="0.15"/>`;
    case "coloured": return `<rect ${r} fill="${SURFACE}"/>`;
    case "footway": return `<rect ${r} fill="${colour("sidewalk")}" stroke="${LINE}" stroke-width="0.1"/>`;
    case "green": case "refuge": return `<rect ${r} fill="${colour(m === "green" ? "median" : "sidewalk")}" stroke="${LINE}" stroke-width="0.1"/>`;
    case "bridge": return `<rect ${r} fill="${colour("cycle_track")}"/><path d="M${f(x)} ${f(y)}H${f(x + w)}M${f(x)} ${f(y + h)}H${f(x + w)}" stroke="${LINE}" stroke-width="0.3"/>`;
    case "bike": return `${road}<g transform="translate(${f(x + w / 2)},${f(mid + 0.15)}) scale(0.5)" fill="none" stroke="${MARK}" stroke-width="0.2"><circle cx="-0.75" r="0.45"/><circle cx="0.75" r="0.45"/><path d="M-0.75 0L-0.2 -0.75L0.45 -0.75L0.75 0"/></g>`;
    default: return "";
  }
}
