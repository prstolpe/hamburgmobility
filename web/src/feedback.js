// Feedback without a server: prefilled GitHub issue and mailto (only if configured in config/project.yaml).
// Feedback never flows into overrides.csv automatically; it is reviewed first (guide 5.4).

function body(profile, pageUrl) {
  return [
    `Abschnitt: ${profile.id}`,
    `Straße: ${profile.name ?? "–"} (${profile.bezirk})`,
    `Soll-Kategorie: ${profile.category.code} (${profile.category.label})`,
    `Version: ${profile.version}`,
    `Link: ${pageUrl}`,
    "",
    "Was stimmt nicht oder fehlt? (bitte keine personenbezogenen Daten)",
    "",
  ].join("\n");
}

export function issueUrl(repo, profile, pageUrl) {
  if (!repo || !/^[\w.-]+\/[\w.-]+$/.test(repo)) return null;
  const p = new URLSearchParams({
    title: `Rückmeldung ${profile.id}: ${profile.name ?? "ohne Namen"} (${profile.category.code})`,
    body: body(profile, pageUrl),
    labels: "rueckmeldung",
  });
  return `https://github.com/${repo}/issues/new?${p.toString()}`;
}

export function mailtoUrl(email, profile, pageUrl) {
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return null;
  const subject = encodeURIComponent(`Rückmeldung ${profile.id} (${profile.category.code})`);
  return `mailto:${email}?subject=${subject}&body=${encodeURIComponent(body(profile, pageUrl))}`;
}
