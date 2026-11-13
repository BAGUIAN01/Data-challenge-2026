"use client";
// Content of the screens: the country summary (sheet over the map), the region preview, the tab
// roots (Régions, Alertes, Plus) and the pushed screens (region, method, sources, pending entries).
import { useEffect, useRef, useState } from "react";
import { BlocEstimation, CarteBande, CarteCalendrier, CarteElevesPays, CarteMatrice, CartePriorites, CarteRisque, CarteTapPays } from "./Cartes";
import { Chevron, IconeApp } from "./icones";
import { dateFr, dateHeureFr, fr } from "@/lib/format";
import { ANNEES_SAISIE, estimerEffectifs } from "@/lib/prevision-effectifs";
import { alerteSeptembre, centaine, PRIORITES, risque, trierRegions } from "@/lib/regles";

export function derniere(saisies, cle) {
  return saisies.filter((s) => s.cle === cle).sort((a, b) => String(b.saisi_le).localeCompare(String(a.saisi_le)))[0] ?? null;
}

// Bounding box of a region path, measured once per path in a hidden SVG.
const boites = new Map();
function boite(d) {
  if (!boites.has(d)) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.cssText = "position:absolute;width:0;height:0;visibility:hidden";
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", d);
    svg.appendChild(p); document.body.appendChild(svg);
    const b = p.getBBox(); svg.remove();
    boites.set(d, [b.x, b.y, b.width, b.height]);
  }
  return boites.get(d);
}

function Silhouette({ jeu, cle, c }) {
  const [box, setBox] = useState(null);
  useEffect(() => { setBox(boite(jeu.carte.regions[cle].d)); }, [jeu, cle]);
  if (!box) return <svg viewBox="0 0 1 1" />;
  const [x, y, w, h] = box, m = Math.max(w, h) * 0.06;
  return <svg viewBox={`${x - m} ${y - m} ${w + 2 * m} ${h + 2 * m}`} aria-hidden="true"><path d={jeu.carte.regions[cle].d} fill={`var(--c${c})`} /></svg>;
}

export function LigneRegion({ jeu, r, onOuvrir, valeur = "risque" }) {
  const v = valeur === "sept" ? alerteSeptembre(r) : risque(r);
  return (
    <button className="row" onClick={() => onOuvrir(r.cle)}>
      <span className="lead"><Silhouette jeu={jeu} cle={r.cle} c={r.priorite} /></span>
      <span className="t"><b>{r.nom}</b><span>{PRIORITES[r.priorite].libelle} · achèvement {fr(r.tap.at(-1), 1)} %</span></span>
      <span className="v num">{v} %<small>{valeur === "sept" ? "septembre" : "risque"}</small></span><Chevron />
    </button>
  );
}

export function ResumePays({ jeu, saisies, nav }) {
  const nb = new Set(saisies.map((s) => s.cle)).size;
  return (
    <>
      <CarteBande jeu={jeu} onOuvrir={nav.ouvrirRegion} />
      <CartePriorites jeu={jeu} onFiltre={(f) => nav.ongletRegions(f)} />
      <CarteElevesPays jeu={jeu} nbSaisies={nb} onSaisies={() => nav.onglet("alertes")} />
      <CarteTapPays jeu={jeu} />
      <div className="sh">Régions<span>de la plus urgente à la moins urgente</span></div>
      <div className="group">{trierRegions(jeu.regions).map((r) => <LigneRegion key={r.cle} jeu={jeu} r={r} onOuvrir={nav.ouvrirRegion} />)}</div>
    </>
  );
}

export function ApercuRegion({ jeu, r, nav }) {
  return (
    <>
      <CarteRisque jeu={jeu} region={r} />
      <div className="btns">
        <button className="btn" onClick={() => nav.ouvrirRegion(r.cle)}>Voir la région</button>
        <button className="btn2" onClick={() => nav.saisir(r.cle)}>Saisir les écoles</button>
      </div>
    </>
  );
}

export function VueRegions({ jeu, filtre, setFiltre, nav }) {
  const n = (f) => jeu.regions.filter(f).length;
  const FIL = [["toutes", "Toutes", jeu.regions.length], ...[1, 2, 3].map((p) => [`p${p}`, `Priorité ${p}`, n((r) => r.priorite === p)]),
    ["eleve", "Risque élevé", n((r) => risque(r) >= jeu.seuils.risque_eleve)]];
  const liste = trierRegions(jeu.regions).filter((r) => filtre === "toutes" || (filtre === "eleve" ? risque(r) >= jeu.seuils.risque_eleve : `p${r.priorite}` === filtre));
  return (
    <>
      <p className="sub" style={{ marginTop: 0 }}>De la plus urgente à la moins urgente</p>
      <CarteMatrice jeu={jeu} onOuvrir={nav.ouvrirRegion} />
      <div className="chips" role="group" aria-label="Filtrer les régions">
        {FIL.map(([k, l, c]) => <button key={k} aria-pressed={filtre === k} onClick={() => setFiltre(k)}>{l} · {c}</button>)}
      </div>
      <div className="group">{liste.map((r) => <LigneRegion key={r.cle} jeu={jeu} r={r} onOuvrir={nav.ouvrirRegion} />)}</div>
    </>
  );
}

function LigneSaisie({ jeu, s, saisies, onOuvrir }) {
  const r = jeu.regions.find((x) => x.cle === s.cle);
  if (!r) return null;
  const e = estimerEffectifs({ region: r, nowcast: jeu.nowcast, annee: s.annee, ecolesOuvertes: s.ecoles_ouvertes });
  const remplacee = saisies.some((x) => x !== s && x.cle === s.cle && x.annee === s.annee && String(x.saisi_le) > String(s.saisi_le));
  return (
    <button className="row" style={{ "--inset": "14px" }} onClick={() => onOuvrir(r.cle)}>
      <span className="t"><b>{r.nom} · {s.annee.replace("-", "/")}</b>
        <span>{fr(s.ecoles_ouvertes)} écoles → ≈ {fr(centaine(e?.centrale))} élèves{remplacee ? " · remplacée" : ""}</span></span>
      <span className="v" style={{ fontSize: 13, color: s.statut === "en_attente" ? "var(--offline)" : "var(--fg-3)" }}>
        {s.statut === "en_attente" ? "en attente" : "envoyée"}</span><Chevron />
    </button>
  );
}

export function VueAlertes({ jeu, saisies, nav }) {
  const triees = [...saisies].sort((a, b) => String(b.saisi_le).localeCompare(String(a.saisi_le)));
  const parSept = [...jeu.regions].sort((a, b) => alerteSeptembre(b) - alerteSeptembre(a));
  return (
    <>
      <p className="sub" style={{ marginTop: 0 }}>Plus l'information arrive, mieux on anticipe.</p>
      <CarteCalendrier jeu={jeu} />
      <div className="sh">Écoles ouvertes saisies<span>{saisies.length ? `${saisies.length} saisie${saisies.length > 1 ? "s" : ""}` : "aucune"}</span></div>
      <div className="group">
        {triees.map((s) => <LigneSaisie key={s.client_id} jeu={jeu} s={s} saisies={saisies} onOuvrir={nav.ouvrirRegion} />)}
        <button className="row plat" onClick={() => nav.saisir(null)}><span className="t"><b>Nouvelle saisie</b></span><Chevron /></button>
      </div>
      <div className="sh">Alerte de septembre<span>probabilité de baisse</span></div>
      <div className="group">{parSept.map((r) => <LigneRegion key={r.cle} jeu={jeu} r={r} valeur="sept" onOuvrir={nav.ouvrirRegion} />)}</div>
      <p className="note">Élevé : 40 % ou plus · moyen : 15 à 39 % · faible : moins de 15 %. Ces probabilités classent bien les régions mais restent approximatives.</p>
    </>
  );
}

export function VuePlus({ jeu, donnees, theme, setTheme, installer, nav }) {
  const { source, recuLe, serveur, saisies, envoi, synchroniser } = donnees;
  const n = saisies.filter((s) => s.statut === "en_attente").length;
  const reseau = serveur === "ok" ? ["En ligne", "var(--ok-txt)"] : serveur === "sans_base" ? ["Base en ligne non configurée", "var(--fg-2)"]
    : serveur === "inconnu" ? ["Vérification…", "var(--fg-3)"] : ["Hors ligne", "var(--offline)"];
  return (
    <>
      <section className="group brand"><IconeApp /><div><b>Décrochage scolaire</b><small>Anticiper par région · Burkina Faso</small></div></section>
      <div className="sh">Synchronisation</div>
      <section className="group">
        <dl className="dl">
          <div><dt>Réseau</dt><dd style={{ color: reseau[1] }}>{reseau[0]}</dd></div>
          <div><dt>Données de ce téléphone</dt><dd>version du {dateFr(jeu.genere_le)}</dd></div>
          <div><dt>Reçues le</dt><dd>{dateHeureFr(recuLe)}</dd></div>
          <div><dt>Origine</dt><dd>{source === "serveur" ? "base en ligne" : "publiées avec l'application"}</dd></div>
        </dl>
        <button className="row plat" onClick={() => nav.pousser("attente")}>
          <span className="t"><b className="l">Saisies en attente d'envoi</b></span><span className="v num">{n === 0 ? "aucune" : n}</span><Chevron />
        </button>
      </section>
      {serveur !== "sans_base" && (
        <section className="group">
          <button className="row plat" onClick={() => synchroniser()} disabled={envoi}>
            <span className="t"><b>{envoi ? "Envoi en cours…" : "Synchroniser maintenant"}</b><span>Données et saisies, dès que le réseau répond</span></span>
          </button>
        </section>
      )}
      <div className="sh">Affichage</div>
      <section className="group">
        <div className="row" style={{ "--inset": "14px" }}><span className="t"><b className="l">Apparence</b></span>
          <span className="seg2" role="group" aria-label="Apparence">
            {[["auto", "Auto"], ["light", "Clair"], ["dark", "Sombre"]].map(([k, l]) => <button key={k} aria-pressed={theme === k} onClick={() => setTheme(k)}>{l}</button>)}
          </span>
        </div>
        {installer && (
          <button className="row plat" onClick={installer.lancer}>
            <span className="t"><b>Installer sur ce téléphone</b><span>{installer.ios ? "Partager, puis « Sur l'écran d'accueil »" : "Comme une application, sans magasin"}</span></span><Chevron />
          </button>
        )}
      </section>
      <div className="sh">À propos</div>
      <section className="group">
        <button className="row plat" onClick={() => nav.pousser("methode")}><span className="t"><b className="l">Méthode et limites</b></span><Chevron /></button>
        <button className="row plat" onClick={() => nav.pousser("sources")}><span className="t"><b className="l">Sources des données</b></span><Chevron /></button>
      </section>
      <p className="note" style={{ textAlign: "center", marginTop: 16 }}>Version des données {jeu.version} · aucune donnée personnelle</p>
    </>
  );
}

// Signed decimal with a real minus sign, French style.
const nb = (v, d = 2) => `${v < 0 ? "−" : ""}${fr(Math.abs(v), d)}`;
const terme = (v, x) => ` ${v < 0 ? "−" : "+"} ${fr(Math.abs(v), 2)} · ${x}`;

// The risk model written out, with a worked example that gives back the probability on screen.
function FormuleRisque({ jeu }) {
  const f = jeu.formule_risque;
  if (!f?.reference) return null;
  const ref = f.reference, r = jeu.regions.find((x) => x.cle === "NORD") ?? jeu.regions[0];
  const I = r.incidents.at(-1), I0 = r.incidents.at(-2), x1 = Math.log1p(I), x2 = x1 - Math.log1p(I0);
  const z = ref.constante + ref.l_inc * x1 + ref.d_l_inc * x2, p = 100 / (1 + Math.exp(-z));
  return (
    <section className="card">
      <div className="ch"><b>La formule du risque</b><span>régression logistique</span></div>
      <p className="formule">p = 1 / (1 + e<sup>−z</sup>)</p>
      <p className="formule num">z = {nb(ref.constante)}{terme(ref.l_inc, "ln(1 + I)")}{terme(ref.d_l_inc, "[ln(1 + I) − ln(1 + I₋₁)]")}</p>
      <ul className="plain">
        <li><b>p</b> : probabilité que les effectifs du primaire baissent de plus de 5 % l'année suivante.</li>
        <li><b>I</b> : incidents de sécurité de l'année scolaire, d'octobre à septembre (ACLED) ; <b>I₋₁</b> : ceux de l'année d'avant. Le second terme mesure l'escalade.</li>
      </ul>
      <p className="para">Exemple, {r.nom} : I = {fr(I)}, I₋₁ = {fr(I0)}, donc z = {nb(z)} et p = {fr(p, 0)} %.</p>
      {f.septembre && f.janvier && (
        <div className="formules-sec">
          <p><b>Alerte de septembre</b> (juillet à septembre connus, J) :<br />
            <span className="num">z = {nb(f.septembre.constante)}{terme(f.septembre.l_inc, "ln(1 + I)")}{terme(f.septembre.d_l_inc, "escalade")}{terme(f.septembre.l_late, "ln(1 + J)")}</span></p>
          <p><b>Alerte de janvier</b> (octobre à décembre connus, R) :<br />
            <span className="num">z = {nb(f.janvier.constante)}{terme(f.janvier.l_inc, "ln(1 + I)")}{terme(f.janvier.d_l_inc, "escalade")}{terme(f.janvier.l_rentree, "ln(1 + R)")}</span></p>
        </div>
      )}
      <p className="foot">Appris sur {f.observations} couples région × année, dont {f.baisses} baisses de plus de 5 %. Niveaux : élevé à partir de {jeu.seuils.risque_eleve} %,
        moyen à partir de {jeu.seuils.risque_moyen} %. Priorité 1 : risque élevé et achèvement sous la moyenne du pays ({fr(jeu.seuils.tap_national, 1)} %).</p>
    </section>
  );
}

export function CorpsMethode({ jeu }) {
  const v = jeu.validation;
  return (
    <>
      <p className="sub" style={{ marginTop: 0 }}>Ce que l'outil sait faire, avec quelle fiabilité, et ce qu'il ne sait pas faire.</p>
      <FormuleRisque jeu={jeu} />
      <section className="card"><div className="ch"><b>Où agir en premier</b></div>
        <p className="para">Achèvement sous la moyenne du pays et risque élevé : priorité 1. Rejouée sur 2019/20 à 2023/24 avec seulement l'information de
          chaque année, elle désignait {v.matrice_regions_pct} % des régions, mais contenait {v.matrice_baisses_pct} % des fortes baisses de l'année suivante
          et {v.matrice_perdus_pct} % des élèves perdus.</p></section>
      <section className="card"><div className="ch"><b>Où le risque monte</b></div>
        <p className="para">Probabilité d'une baisse des effectifs de plus de 5 %, à partir de la violence. Fiabilité {fr(v.auc_reference, 2)} pour la référence,
          {" "}{fr(v.auc_septembre, 2)} fin septembre, {fr(v.auc_janvier, 2)} début janvier (1 = parfait, 0,5 = hasard), mesurée sur des années que le modèle
          n'avait pas vues.</p></section>
      <section className="card"><div className="ch"><b>Combien d'élèves</b></div>
        <p className="para">Avec le nombre d'écoles ouvertes à la rentrée, l'erreur sur les effectifs tombe à ± {fr(jeu.nowcast.erreur_pct, 1)} %, contre
          {" "}± {fr(jeu.nowcast.erreur_persistance_pct, 1)} % en reprenant les chiffres de l'année d'avant. Vérifié à un an de l'annuaire seulement.</p></section>
      <section className="card"><div className="ch"><b>Ce que l'outil ne sait pas faire</b></div>
        <ul className="plain">
          <li>Prévoir à l'aveugle de combien le taux d'achèvement va bouger : aucun modèle testé ne bat « comme l'an passé ».</li>
          <li>Voir les réouvertures d'écoles : ce sont des décisions de l'État, absentes des données.</li>
          <li>Descendre aux provinces ou aux écoles : les données du concours s'arrêtent aux 13 régions.</li>
          <li>Mesurer directement l'abandon : il n'y a ni redoublants ni abandons dans les données ; on utilise des substituts.</li>
        </ul></section>
      <section className="card"><div className="ch"><b>Sans réseau</b></div>
        <p className="para">Les données sont enregistrées sur ce téléphone et l'application garde ses écrans et les fiches PDF : tout s'ouvre sans réseau après
          une première visite. Les saisies restent sur le téléphone et partent vers la base en ligne au retour du réseau, sans être perdues ni comptées deux fois.</p></section>
    </>
  );
}

export function CorpsSources() {
  const S = [["DGESS", "Annuaires statistiques, données du Data Challenge Burkina 2026"], ["ACLED", "Incidents de sécurité, via HDX"], ["IGB", "Limites des régions"],
    ["Cadre Harmonisé", "Faim, phase 3 ou plus"], ["EDS 2021", "Instruction des femmes, grossesses précoces"], ["CONASUR", "Personnes déplacées internes"], ["INSD, EHCVM 2021", "Pauvreté"]];
  return (
    <>
      <section className="group">{S.map(([a, b]) => <div key={a} className="row" style={{ "--inset": "14px" }}><span className="t"><b>{a}</b><span>{b}</span></span></div>)}</section>
      <p className="note">Calculs de l'équipe. Aucune donnée personnelle. Les données servent uniquement au concours.</p>
    </>
  );
}

export function CorpsAttente({ jeu, saisies, nav }) {
  const att = saisies.filter((s) => s.statut === "en_attente");
  return (
    <>
      <p className="sub" style={{ marginTop: 0 }}>Gardées sur ce téléphone. Elles partent au retour du réseau, une seule fois ; rien n'est perdu.</p>
      <div className="group">
        {att.length ? att.map((s) => <LigneSaisie key={s.client_id} jeu={jeu} s={s} saisies={saisies} onOuvrir={nav.ouvrirRegion} />)
          : <div className="row plat"><span className="t"><b>Rien en attente</b><span>Tout est envoyé.</span></span></div>}
      </div>
    </>
  );
}

// The one write gesture: number of schools open at the start of the year, for a region and a year.
export function FormSaisie({ jeu, cleInitiale, onEnregistrer }) {
  const regions = trierRegions(jeu.regions);
  const [cle, setCle] = useState(cleInitiale ?? regions[0].cle);
  const [annee, setAnnee] = useState(ANNEES_SAISIE[0]);
  const [texte, setTexte] = useState("");
  const r = jeu.regions.find((x) => x.cle === cle), n = Number(texte), valide = texte !== "" && Number.isInteger(n) && n > 0 && n < 100000;
  const champ = useRef(null);
  // The number pad opens once the sheet has slid in.
  useEffect(() => { const t = setTimeout(() => champ.current?.focus({ preventScroll: true }), 420); return () => clearTimeout(t); }, []);
  return (
    <>
      <section className="group">
        <div className="row plat"><span className="t"><b className="l">Région</b></span>
          <select className="sel" value={cle} onChange={(e) => setCle(e.target.value)} aria-label="Région">
            {regions.map((x) => <option key={x.cle} value={x.cle}>{x.nom}</option>)}
          </select></div>
        <div className="row plat"><span className="t"><b className="l">Année</b></span>
          <span className="seg2" role="group" aria-label="Année scolaire">
            {ANNEES_SAISIE.map((a) => <button key={a} aria-pressed={a === annee} onClick={() => setAnnee(a)}>{a.replace("-", "/")}</button>)}
          </span></div>
        <div className="field">
          <label htmlFor="saisie-ecoles">Nombre d'écoles ouvertes</label>
          <input id="saisie-ecoles" ref={champ} inputMode="numeric" pattern="[0-9]*" autoComplete="off" placeholder={fr(r.ecoles.at(-1))} value={texte}
            onChange={(e) => setTexte(e.target.value.replace(/\D/g, "").slice(0, 6))} />
          <span className="note" style={{ margin: 0 }}>Annuaire 2024/25 : {fr(r.ecoles.at(-1))} écoles, {fr(r.eleves.at(-1))} élèves.</span>
        </div>
      </section>
      {valide && (
        <section className="card"><div className="ch"><b>Élèves attendus</b><span>{annee.replace("-", "/")}</span></div>
          <BlocEstimation jeu={jeu} region={r} annee={annee} ecoles={n} /></section>
      )}
      {valide && <button className="btn" onClick={() => onEnregistrer({ cle, annee, ecoles_ouvertes: n })}>Enregistrer</button>}
      {!valide && <p className="note">Tapez le nombre d'écoles ouvertes : les élèves attendus s'affichent aussitôt.</p>}
      <p className="note" style={{ marginTop: 12 }}>Enregistré sur ce téléphone, même sans réseau ; part vers la base en ligne au retour du réseau, une seule fois.</p>
    </>
  );
}
