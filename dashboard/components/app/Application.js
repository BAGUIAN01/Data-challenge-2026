"use client";
// The dashboard as one app: map with a bottom sheet (side panel on a large screen), four tabs, each
// with its own stack of screens. Navigation follows the phone: a pushed screen adds a history entry,
// so the phone's back button (or gesture) closes it; a region screen has its own address (#region/X)
// that reopens it, even without network (same page, kept by the service worker).
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useDonnees } from "../DonneesProvider";
import CarteRegions from "./CarteRegions";
import Ecran from "./Ecran";
import Feuille, { hauteurCran } from "./Feuille";
import FicheRegion from "./Fiche";
import { IcAlertes, IcCarte, IconeApp, IcPlus, IcRegions } from "./icones";
import { ApercuRegion, CorpsAttente, CorpsMethode, CorpsSources, FormSaisie, ResumePays, VueAlertes, VuePlus, VueRegions } from "./Vues";
import { dateFr, dateHeureFr, fr } from "@/lib/format";
import { couches, PRIORITES } from "@/lib/regles";

const ONGLETS = [["carte", "Carte", IcCarte], ["regions", "Régions", IcRegions], ["alertes", "Alertes", IcAlertes], ["plus", "Plus", IcPlus]];
const TITRES = { carte: "Carte", regions: "Régions", alertes: "Alertes", plus: "Plus" };
const TITRES_ECRANS = { methode: "Méthode", sources: "Sources", attente: "En attente d'envoi" };
const DUREE = 450;
const nSaisies = (n) => (n === 1 ? "1 saisie" : `${n} saisies`);

export default function Application() {
  const donnees = useDonnees();
  if (!donnees.jeu) {
    return (
      <div className="lancement" role="status">
        <IconeApp /><b>Décrochage scolaire</b>
        <p>{donnees.serveur === "inconnu" ? "Lecture des données de ce téléphone…"
          : "Aucune donnée sur ce téléphone et pas de réseau. Ouvrez l'application une première fois avec une connexion : elle fonctionnera ensuite sans réseau."}</p>
      </div>
    );
  }
  return <Coque donnees={donnees} />;
}

// Banner: where the data come from and what waits for the network. Hidden when all is in order.
function etatBandeau({ serveur, recuLe, saisies, envoi }, envoye) {
  const n = saisies.filter((s) => s.statut === "en_attente").length;
  if (envoi) return { cls: "send", etat: "envoi", texte: `Envoi de ${nSaisies(n)}…` };
  if (serveur === "injoignable") {
    return { cls: "off", etat: "hors-ligne", texte: `Hors ligne · ${n ? `${nSaisies(n)} en attente d'envoi` : `données de ce téléphone, reçues le ${dateHeureFr(recuLe)}`}` };
  }
  if (serveur === "erreur") return { cls: "info", etat: "erreur", texte: `La base en ligne ne répond pas · données de ce téléphone${n ? `, ${nSaisies(n)} en attente` : ""}` };
  if (serveur === "sans_base" && n) return { cls: "info", etat: "sans-base", texte: `${nSaisies(n)} sur ce téléphone · base en ligne non configurée` };
  if (n) return { cls: "info", etat: "attente", texte: `${nSaisies(n)} en attente d'envoi` };
  if (envoye) return { cls: "ok", etat: "envoye", texte: "À jour · tout est envoyé" };
  return { cls: "hide", etat: serveur === "ok" ? "a-jour" : serveur === "sans_base" ? "sans-base" : "inconnu", texte: "" };
}

function Coque({ donnees }) {
  const { jeu, saisies, serveur, envoi, ajouterSaisie, retirerSaisie, synchroniser } = donnees;
  const [onglet, setOnglet] = useState("carte");
  const [piles, setPiles] = useState({ carte: [], regions: [], alertes: [], plus: [] });
  const [modal, setModal] = useState(null);
  const [snack, setSnack] = useState(null);
  const [couche, setCouche] = useState(() => (jeu.score_global ? "score" : "risque"));
  const [apercu, setApercu] = useState(null);
  const [cran, setCran] = useState("bas");
  const [filtre, setFiltre] = useState("toutes");
  const [commande, setCommande] = useState({ n: 0 });
  const [theme, setThemeEtat] = useState("auto");
  const [q, setQ] = useState("");
  const [installer, setInstaller] = useState(null);
  const [envoye, setEnvoye] = useState(false);
  const etat = useRef({});
  etat.current = { ...etat.current, onglet, modal, cran };
  if (!etat.current.piles) etat.current.piles = piles;
  const ignorer = useRef(0), compteur = useRef(0), tabsRef = useRef(null), barreRef = useRef(null), zoneRef = useRef(null), envoiAvant = useRef(false);
  const COUCHES = useMemo(() => couches(jeu), [jeu]);
  const enAttente = saisies.filter((s) => s.statut === "en_attente").length;

  // ---------- Stacks ----------
  const ecrirePiles = useCallback((f) => { const p = f(etat.current.piles); etat.current.piles = p; setPiles(p); }, []);
  // dejaDansHistorique: the browser already added the entry (a link to #region/X was followed).
  const pousser = useCallback((type, params = {}, dejaDansHistorique = false) => {
    const id = ++compteur.current, t = etat.current.onglet;
    ecrirePiles((p) => ({ ...p, [t]: [...p[t], { id, type, params }] }));
    if (!dejaDansHistorique) history.pushState({ ecran: id }, "", type === "region" ? `#region/${params.cle}` : location.href);
  }, [ecrirePiles]);
  const depiler = useCallback((t = etat.current.onglet) => {
    const top = [...etat.current.piles[t]].reverse().find((e) => !e.sortant);
    if (!top) return false;
    ecrirePiles((p) => ({ ...p, [t]: p[t].map((e) => (e.id === top.id ? { ...e, sortant: true } : e)) }));
    setTimeout(() => ecrirePiles((p) => ({ ...p, [t]: p[t].filter((e) => e.id !== top.id) })), DUREE);
    return true;
  }, [ecrirePiles]);
  const viderPile = useCallback((t) => {
    const n = etat.current.piles[t].filter((e) => !e.sortant).length;
    if (!n) return;
    for (let i = 0; i < n; i++) depiler(t);
    ignorer.current++;
    history.go(-n);
  }, [depiler]);
  const glisseRetour = useCallback(() => { ignorer.current++; depiler(); history.back(); }, [depiler]);

  // ---------- Modal sheets and snackbar ----------
  const ouvrirModal = useCallback((m) => { setModal({ ...m, ferme: false }); history.pushState({ modal: true }, "", location.href); }, []);
  const fermerModal = useCallback(() => {
    if (!etat.current.modal || etat.current.modal.ferme) return false;
    setModal((m) => m && { ...m, ferme: true });
    setTimeout(() => setModal((m) => (m?.ferme ? null : m)), 400);
    return true;
  }, []);
  const montrerSnack = useCallback((texte, action, fn) => setSnack({ id: Date.now(), texte, action, fn, visible: true }), []);
  useEffect(() => {
    if (!snack?.visible) return;
    const t = setTimeout(() => setSnack((s) => s && s.id === snack.id && { ...s, visible: false }), snack.action ? 5000 : 3200);
    return () => clearTimeout(t);
  }, [snack]);

  useEffect(() => {
    const surPop = () => {
      if (ignorer.current > 0) { ignorer.current--; return; }
      if (fermerModal()) return;
      depiler();
    };
    const surTouche = (e) => { if (e.key === "Escape" && (etat.current.modal || etat.current.piles[etat.current.onglet].some((x) => !x.sortant))) history.back(); };
    window.addEventListener("popstate", surPop);
    window.addEventListener("keydown", surTouche);
    return () => { window.removeEventListener("popstate", surPop); window.removeEventListener("keydown", surTouche); };
  }, [depiler, fermerModal]);

  // ---------- Gestures of the app ----------
  const changerOnglet = useCallback((t) => {
    if (t === etat.current.onglet) {
      if (etat.current.piles[t].some((e) => !e.sortant)) viderPile(t);
      else document.querySelector(`#t-${t} .screen:not(.pushed) .sc, #t-${t} .sh-in`)?.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    etat.current.onglet = t;
    setOnglet(t);
    setSnack((s) => s && { ...s, visible: false });
  }, [viderPile]);
  const ouvrirRegion = useCallback((cle) => pousser("region", { cle }), [pousser]);
  const apercevoir = useCallback((cle) => {
    if (etat.current.onglet !== "carte") { etat.current.onglet = "carte"; setOnglet("carte"); }
    viderPile("carte");
    setApercu(cle); setCran("mi"); setQ("");
    setCommande((c) => ({ n: c.n + 1, type: "region", cle }));
  }, [viderPile]);
  const fermerApercu = useCallback(() => { setApercu(null); setCran("bas"); setCommande((c) => ({ n: c.n + 1, type: "pays" })); }, []);
  const saisir = useCallback((cle) => ouvrirModal({ type: "saisie", cle }), [ouvrirModal]);
  const enregistrer = useCallback(async (s) => {
    history.back();
    const ligne = await ajouterSaisie(s);
    navigator.vibrate?.(10);
    // True whatever the network does next: the entry is on the phone and leaves when the server answers.
    const suite = serveur === "sans_base" ? "gardé sur ce téléphone (base en ligne non configurée)" : "enregistré sur ce téléphone, part dès que le réseau répond";
    montrerSnack(`${fr(s.ecoles_ouvertes)} écoles : ${suite}.`, "Annuler", async () => {
      if (!(await retirerSaisie(ligne.client_id))) montrerSnack("Déjà envoyée : faites une nouvelle saisie pour corriger.");
    });
  }, [ajouterSaisie, retirerSaisie, montrerSnack, serveur]);
  const ongletRegions = useCallback((f) => { setFiltre(f); changerOnglet("regions"); }, [changerOnglet]);
  const nav = useMemo(() => ({ pousser, ouvrirRegion, apercevoir, saisir, onglet: changerOnglet, ongletRegions }),
    [pousser, ouvrirRegion, apercevoir, saisir, changerOnglet, ongletRegions]);

  // Visible part of the map, for framing: between the floating controls and the sheet + tab bar.
  const marges = useCallback(() => {
    if (matchMedia("(min-width: 900px)").matches) return { haut: 140, bas: 16 };
    const H = tabsRef.current?.clientHeight ?? 600, barre = barreRef.current?.offsetHeight ?? 54;
    return { haut: 140, bas: hauteurCran(etat.current.cran, H) + barre + 8 };
  }, []);

  // ---------- Theme, installation, deep link, send feedback ----------
  useEffect(() => {
    try { const t = localStorage.getItem("theme"); if (t === "light" || t === "dark") setThemeEtat(t); } catch { /* private mode */ }
  }, []);
  const setTheme = useCallback((t) => {
    setThemeEtat(t);
    if (t === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
    try { if (t === "auto") localStorage.removeItem("theme"); else localStorage.setItem("theme", t); } catch { /* private mode */ }
  }, []);
  useEffect(() => {
    const autonome = matchMedia("(display-mode: standalone)").matches || navigator.standalone;
    if (autonome) return undefined;
    if (/iphone|ipad|ipod/i.test(navigator.userAgent)) {
      setInstaller({ ios: true, lancer: () => montrerSnack("Dans Safari : touchez Partager, puis « Sur l'écran d'accueil ».") });
      return undefined;
    }
    const surInvite = (e) => {
      e.preventDefault();
      setInstaller({ ios: false, lancer: async () => { e.prompt(); await e.userChoice.catch(() => null); setInstaller(null); } });
    };
    window.addEventListener("beforeinstallprompt", surInvite);
    return () => window.removeEventListener("beforeinstallprompt", surInvite);
  }, [montrerSnack]);
  const lienOuvert = useRef(false);
  useEffect(() => {
    if (lienOuvert.current) return;
    lienOuvert.current = true;
    const m = location.hash.match(/^#region\/([A-Z]+)$/);
    if (m && jeu.regions.some((r) => r.cle === m[1])) { history.replaceState(null, "", location.pathname); pousser("region", { cle: m[1] }); }
  }, [jeu, pousser]);
  // A link to #region/X followed inside the app (no reload): open that region on top.
  useEffect(() => {
    const surHash = () => {
      const m = location.hash.match(/^#region\/([A-Z]+)$/);
      if (!m || !jeu.regions.some((r) => r.cle === m[1])) return;
      const top = [...etat.current.piles[etat.current.onglet]].reverse().find((e) => !e.sortant);
      if (top?.type === "region" && top.params.cle === m[1]) return;
      pousser("region", { cle: m[1] }, true);
    };
    window.addEventListener("hashchange", surHash);
    return () => window.removeEventListener("hashchange", surHash);
  }, [jeu, pousser]);
  useEffect(() => {
    if (envoiAvant.current && !envoi && enAttente === 0) {
      setEnvoye(true);
      const t = setTimeout(() => setEnvoye(false), 2000);
      envoiAvant.current = envoi;
      return () => clearTimeout(t);
    }
    envoiAvant.current = envoi;
    return undefined;
  }, [envoi, enAttente]);

  const bandeau = etatBandeau(donnees, envoye);

  const titreDe = (e) => (e.type === "region" ? jeu.regions.find((r) => r.cle === e.params.cle)?.nom ?? "Région" : TITRES_ECRANS[e.type]);
  const regionApercu = apercu && jeu.regions.find((r) => r.cle === apercu);
  // On a large screen the map stays visible: it outlines the region open in the panel.
  const ecranRegion = [...piles[onglet]].reverse().find((e) => !e.sortant && e.type === "region");
  const selection = apercu ?? ecranRegion?.params.cle ?? null;
  const resultats = q.trim()
    ? jeu.regions.filter((r) => [r.nom, r.ancienne].some((s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .includes(q.trim().normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()))).slice(0, 5)
    : null;

  function ecranPousse(e, i, pile, t) {
    const prec = i === 0 ? TITRES[t] : titreDe(pile[i - 1]);
    const couvert = pile.slice(i + 1).some((x) => !x.sortant);
    const commun = { key: e.id, id: e.type, pousse: true, sortant: e.sortant, couvert, titre: titreDe(e),
      retour: prec.length > 14 ? "Retour" : prec, onRetour: () => history.back(), onGlisseRetour: glisseRetour };
    if (e.type === "region") {
      const cle = e.params.cle;
      return (
        <Ecran {...commun} className="doc" barre={
          <div className="btns">
            <button className="btn" onClick={() => saisir(cle)}>Saisir les écoles</button>
            <a className="btn2" href={`/fiches/${cle}.pdf`} target="_blank" rel="noopener">Ouvrir la fiche</a>
          </div>}>
          <FicheRegion jeu={jeu} r={jeu.regions.find((r) => r.cle === cle)} saisies={saisies} onMethode={() => pousser("methode")} />
        </Ecran>
      );
    }
    if (e.type === "methode") return <Ecran {...commun}><CorpsMethode jeu={jeu} /></Ecran>;
    if (e.type === "sources") return <Ecran {...commun}><CorpsSources /></Ecran>;
    return <Ecran {...commun}><CorpsAttente jeu={jeu} saisies={saisies} nav={nav} /></Ecran>;
  }
  const couvertRacine = (t) => piles[t].some((x) => !x.sortant);
  const sousTitre = serveur === "ok" ? `à jour, version du ${dateFr(jeu.genere_le)}` : `données de ce téléphone, version du ${dateFr(jeu.genere_le)}`;

  return (
    <div className="app" data-onglet={onglet}>
      <div className="stat-sp" />
      <button className={`banner ${bandeau.cls}`} data-etat={bandeau.etat} aria-live="polite" onClick={() => ouvrirModal({ type: "reseau" })}
        tabIndex={bandeau.cls === "hide" ? -1 : 0}>
        {bandeau.cls === "off" && <i />}<span>{bandeau.texte}</span>
      </button>
      <div className="zone" ref={zoneRef}>
        <div className="zone-carte">
          <CarteRegions jeu={jeu} classe={COUCHES[couche].classe} selection={selection} onChoisir={apercevoir} commande={commande} marges={marges} />
          <div className="ftop">
            <label className="search">
              <IconeApp />
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Chercher une région" aria-label="Chercher une région" autoComplete="off" enterKeyHint="search" />
            </label>
            {resultats && (
              <div className="results">
                {resultats.length ? resultats.map((r) => (
                  <button key={r.cle} className="row" onClick={() => apercevoir(r.cle)}>
                    <span className="t"><b>{r.nom}</b><span>ancienne {r.ancienne} · {PRIORITES[r.priorite].libelle.toLowerCase()}</span></span>
                  </button>
                )) : <div className="row" style={{ "--inset": "14px" }}><span className="t"><b>Aucune région</b><span>pour « {q} »</span></span></div>}
              </div>
            )}
            <div className="ctrl">
              <div className="seg" role="group" aria-label="Couche de la carte">
                {Object.entries(COUCHES).map(([k, c]) => <button key={k} aria-pressed={couche === k} onClick={() => setCouche(k)}>{c.nom}</button>)}
              </div>
              <div className="mleg">{COUCHES[couche].legende.map((l, i) => <span key={l}><i className="m" style={{ "--c": `var(--c${i + 1})` }} />{l}</span>)}</div>
            </div>
          </div>
        </div>
        <div className="panneau">
          <div className="tabs" ref={tabsRef}>
            <section className="tab" id="t-carte" hidden={onglet !== "carte"}>
              <div className={`screen racine-carte${couvertRacine("carte") ? " covered" : ""}`} data-ecran="carte">
                <Feuille cran={cran} setCran={setCran} defilement={apercu}
                  tete={regionApercu ? (
                    <>
                      <div className="tt"><b>{regionApercu.nom}</b>
                        <span><i className="m" style={{ "--c": `var(--c${regionApercu.priorite})` }} />{PRIORITES[regionApercu.priorite].libelle}, {PRIORITES[regionApercu.priorite].sous} · ancienne {regionApercu.ancienne}</span></div>
                      <button className="sh-x" onClick={fermerApercu}>Fermer</button>
                    </>
                  ) : <div className="tt"><b>Burkina Faso</b><span>13 régions · {sousTitre}</span></div>}>
                  {regionApercu ? <ApercuRegion jeu={jeu} r={regionApercu} nav={nav} /> : <ResumePays jeu={jeu} saisies={saisies} nav={nav} />}
                </Feuille>
              </div>
              {piles.carte.map((e, i, p) => ecranPousse(e, i, p, "carte"))}
            </section>
            <section className="tab" id="t-regions" hidden={onglet !== "regions"}>
              <Ecran titre="Régions" id="regions" couvert={couvertRacine("regions")}><VueRegions jeu={jeu} filtre={filtre} setFiltre={setFiltre} nav={nav} /></Ecran>
              {piles.regions.map((e, i, p) => ecranPousse(e, i, p, "regions"))}
            </section>
            <section className="tab" id="t-alertes" hidden={onglet !== "alertes"}>
              <Ecran titre="Alertes" id="alertes" couvert={couvertRacine("alertes")}><VueAlertes jeu={jeu} saisies={saisies} nav={nav} /></Ecran>
              {piles.alertes.map((e, i, p) => ecranPousse(e, i, p, "alertes"))}
            </section>
            <section className="tab" id="t-plus" hidden={onglet !== "plus"}>
              <Ecran titre="Plus" id="plus" couvert={couvertRacine("plus")}>
                <VuePlus jeu={jeu} donnees={donnees} theme={theme} setTheme={setTheme} installer={installer} nav={nav} />
              </Ecran>
              {piles.plus.map((e, i, p) => ecranPousse(e, i, p, "plus"))}
            </section>
          </div>
          <nav className="tabbar" aria-label="Onglets" ref={barreRef}>
            {ONGLETS.map(([k, l, Ic]) => (
              <button key={k} aria-current={onglet === k ? "page" : undefined} onClick={() => changerOnglet(k)}>
                <Ic />{l}
                {k === "alertes" && enAttente > 0 && <span className="bdg" aria-label={`${nSaisies(enAttente)} en attente d'envoi`}>{enAttente}</span>}
              </button>
            ))}
          </nav>
        </div>
      </div>
      <div className={`snack${snack?.visible ? " in" : ""}`} role="status">
        <span>{snack?.texte}</span>
        {snack?.action && <button onClick={() => { const f = snack.fn; setSnack((s) => s && { ...s, visible: false }); f?.(); }}>{snack.action}</button>}
      </div>
      {modal && (
        <Modale ferme={modal.ferme}>
          {modal.type === "saisie" ? (
            <div className="ps" role="dialog" aria-modal="true" aria-label="Saisir les écoles ouvertes">
              <i className="grab" />
              <div className="ps-h"><h2>Écoles ouvertes à la rentrée</h2><button className="sh-x" onClick={() => history.back()}>Fermer</button></div>
              <FormSaisie jeu={jeu} cleInitiale={modal.cle} onEnregistrer={enregistrer} />
            </div>
          ) : (
            <div className="ps" role="dialog" aria-modal="true" aria-label="État du réseau">
              <i className="grab" />
              <div className="ps-h"><h2>{serveur === "ok" ? "En ligne" : serveur === "sans_base" ? "Base en ligne non configurée" : "Hors ligne"}</h2></div>
              <p className="sub" style={{ marginTop: 0 }}>
                {serveur === "ok" ? "Les données et les saisies se synchronisent avec la base en ligne."
                  : serveur === "sans_base" ? "Les données sont celles publiées avec l'application ; les saisies restent sur ce téléphone."
                    : "Vous travaillez sur les données de ce téléphone. Les saisies partent au retour du réseau, une seule fois ; rien n'est perdu."}
              </p>
              <section className="group"><dl className="dl">
                <div><dt>Données de ce téléphone</dt><dd>version du {dateFr(jeu.genere_le)}</dd></div>
                <div><dt>Saisies en attente d'envoi</dt><dd>{enAttente === 0 ? "aucune" : enAttente}</dd></div>
              </dl></section>
              <div className="btns">
                <button className="btn2" onClick={() => synchroniser()}>Réessayer</button>
                <button className="btn" onClick={() => history.back()}>Fermer</button>
              </div>
            </div>
          )}
        </Modale>
      )}
    </div>
  );
}

function Modale({ ferme, children }) {
  const [dedans, setDedans] = useState(false);
  useEffect(() => { const r = requestAnimationFrame(() => requestAnimationFrame(() => setDedans(true))); return () => cancelAnimationFrame(r); }, []);
  return (
    <div className={`modal${dedans && !ferme ? " in" : ""}`}>
      <div className="scrim" onClick={() => history.back()} />
      {children}
    </div>
  );
}
