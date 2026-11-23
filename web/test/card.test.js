// Image card content (prompt 28): title, one sentence, sketch, alt text and deep link from the data – no "undefined".
import { describe, expect, it } from "vitest";
import { altText, cardHtml, FORMATS, junctionCard, placeCard, segmentCard } from "../src/card_content.js";

const META = {
  data_date: "2026-10-28", categories: { GOW50: { label: "Hauptstraße mit Tempo 50" } },
  cycling: { elements: { sidewalk: { label: "Gehweg", color: "#d9d4c7" }, carriageway: { label: "Fahrbahn", color: "#555b61" } }, junction_group: {} },
};
const SEG = {
  id: "seg_fa69", name: "Hoheluftchaussee", bezirk: "Eimsbüttel", length_m: 179.2, category: { code: "GOW50", label: "Stadtstraße 50" },
  ist: { speed_kmh: 50, cycling: "baulicher Radweg" }, crosssection: { width_median_m: 47.5 },
  cycling: { profile: { fit_text: "passt in die Straße", required_m: 13, available_m: 36.8,
    elements: [{ element: "sidewalk", width_m: 3, side: "left" }, { element: "carriageway", width_m: 7, side: "centre" }, { element: "sidewalk", width_m: 3, side: "right" }] } },
};
const noUndefined = (c) => { for (const v of Object.values(c)) expect(String(v)).not.toContain("undefined"); };

describe("card content", () => {
  it("segment: plain category, today, cross-section and v2 deep link", () => {
    const c = segmentCard(SEG, META);
    expect(c.sentence).toBe("Ziel: Hauptstraße mit Tempo 50. Heute: Tempo 50, Rad: baulicher Radweg.");
    expect(c.sketch).toContain("<svg");
    expect(c.altSketch).toBe("Querschnitt im Ziel: Gehweg 3,0 m, Fahrbahn 7,0 m, Gehweg 3,0 m.");
    expect(c.link).toBe("#karte?v=2&seg=seg_fa69");
    noUndefined(c);
  });

  it("segment without drawing: no sketch, still a sentence", () => {
    const c = segmentCard({ ...SEG, cycling: null, ist: {} }, META);
    expect(c.sketch).toBe("");
    expect(c.sentence).toBe("Ziel: Hauptstraße mit Tempo 50. Heute: Tempo unbekannt.");
    noUndefined(c);
  });

  it("junction: target, today, rebuild; node link", () => {
    const c = junctionCard({ id: 7, names: "Heußweg / Lutterothstraße", bezirk: "Eimsbüttel", soll: { text: "Vorfahrt mit erhöhter Fahrbahn" },
      ist: { text: "Ampel" }, action_needed: true, legs: [], treatment: [] }, META);
    expect(c.title).toBe("Kreuzung Heußweg / Lutterothstraße");
    expect(c.sentence).toBe("Ziel: Vorfahrt mit erhöhter Fahrbahn. Heute: Ampel. Umbau nötig.");
    expect(c.link).toBe("#karte?v=2&node=7");
  });

  it("place: measures with the dash note, status date", () => {
    const c = placeCard({ id: "schanze_verkehrsberuhigt", title: "Verkehrsberuhigte Schanze", kind_plain: "Vorschlag", initiator: "Bürgerbegehren",
      status: "Unterschriften werden gesammelt", status_date: "2026-09-25", theme: { pattern: { pz: "dashed" } },
      measures: [{ measure: "cs", label: "Fahrradstraße" }, { measure: "pz", label: "Fußgängerzone" }, { measure: "cs", label: "Fahrradstraße" }] });
    expect(c.sentence).toBe("Fahrradstraße, Fußgängerzone (gestrichelt). Stand 25.09.2026: Unterschriften werden gesammelt.");
    expect(c.link).toBe("#karte?v=2&place=schanze_verkehrsberuhigt");
  });

  it("alt text names the item, the sentence, the sketch and the status date", () => {
    const alt = altText(segmentCard(SEG, META), META);
    expect(alt).toContain("Karte: Hoheluftchaussee (Eimsbüttel · 179 m), hervorgehoben.");
    expect(alt).toContain("Querschnitt im Ziel: Gehweg 3,0 m");
    expect(alt).toContain("Datenstand 28.10.2026");
    expect(alt).not.toContain("undefined");
  });

  it("formats: link preview, portrait, A4 inset at 300 dpi", () => {
    expect(FORMATS.og.width * FORMATS.og.scale).toBe(1200);
    expect(FORMATS.portrait.height * FORMATS.portrait.scale).toBe(1350);
    const mm = (px) => (px * FORMATS.a4.scale / 300) * 25.4;
    expect(Math.round(mm(FORMATS.a4.width))).toBe(140);
    expect(Math.round(mm(FORMATS.a4.height))).toBe(100);
  });

  it("the card carries sources, data date and the deep link", () => {
    const html = cardHtml(segmentCard(SEG, META), META, "og");
    expect(html).toContain("OpenStreetMap-Beitragende (ODbL)");
    expect(html).toContain("Datenstand 28.10.2026");
    expect(html).toContain("hamburgmobility.de/#karte?v=2&amp;seg=seg_fa69");
  });
});
