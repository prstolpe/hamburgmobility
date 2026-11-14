// Variant A "Karte zuerst" (prompt 24, A3): the map is the start page; themes above the map, legend in words to the
// left, profile in three levels to the right (mobile: sheet from below).
import { bindSearch, loadData, mountMapView } from "../shared/mapview.js";

const { meta, district, search } = await loadData();
document.querySelector("#datestand").textContent = `Datenstand ${new Date(meta.data_date).toLocaleDateString("de-DE")}`;
const view = mountMapView(document.querySelector("#main"), { meta, district, page: "#karte" });
bindSearch(document.querySelector("#q"), document.querySelector("#q-list"), search, (h) => {
  const [w, s, e, n] = h.bbox;
  view.openSegment(h.ids[0], { fly: true, at: [(w + e) / 2, (s + n) / 2] });
});
window.proto = { view, meta, district };
