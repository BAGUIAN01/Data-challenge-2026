"use client";
// Local-first data layer. Order of reading, always:
//   1. the device database (instant, works without network);
//   2. the server (Neon) when it answers: the device copy is replaced if the version changed;
//   3. the snapshot shipped with the app, only if the device has nothing yet.
// Field entries go to the device first (outbox) and leave when the server answers, once the
// few seconds in which the user can still cancel them have passed.
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { db } from "@/lib/db-locale";

const Contexte = createContext(null);
const DELAI_MS = 8000;
// Window in which a new entry can be cancelled: it does not leave before.
export const DELAI_ANNULATION_MS = 6000;

async function chercher(url, options = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), DELAI_MS);
  try {
    return await fetch(url, { cache: "no-store", ...options, signal: ctrl.signal });
  } finally {
    clearTimeout(t);
  }
}

function uuid() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16));
  b[6] = (b[6] & 0x0f) | 0x40;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

export function DonneesProvider({ children }) {
  const [etat, setEtat] = useState({ jeu: null, source: null, recuLe: null, serveur: "inconnu", message: null });
  const [saisies, setSaisies] = useState([]);
  const [envoi, setEnvoi] = useState(false);
  const enCours = useRef(false);

  const relireSaisies = useCallback(async () => setSaisies(await db.saisies.toArray()), []);

  const enregistrer = useCallback(async (donnees, source) => {
    const ligne = { cle: "courant", donnees, version: donnees.version, source, recu_le: new Date().toISOString() };
    await db.jeu.put(ligne);
    return ligne;
  }, []);

  const envoyerSaisies = useCallback(async () => {
    const mures = Date.now() - DELAI_ANNULATION_MS;
    const attente = (await db.saisies.where("statut").equals("en_attente").toArray()).filter((s) => Date.parse(s.saisi_le) <= mures);
    if (!attente.length) return { envoyees: 0 };
    setEnvoi(true);
    try {
      const rep = await chercher("/api/saisies", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ saisies: attente.map(({ statut, ...s }) => s) }),
      });
      const corps = await rep.json().catch(() => ({}));
      if (!rep.ok) throw Object.assign(new Error(corps.message || "Envoi impossible"), { corps });
      await db.saisies.where("client_id").anyOf(corps.recues ?? []).modify({ statut: "envoyee" });
      return { envoyees: corps.recues?.length ?? 0 };
    } finally {
      setEnvoi(false);
    }
  }, []);

  const recevoirSaisies = useCallback(async () => {
    const rep = await chercher("/api/saisies");
    if (!rep.ok) return;
    const { saisies: distantes = [] } = await rep.json();
    for (const s of distantes) {
      if (!(await db.saisies.get(s.client_id))) await db.saisies.put({ ...s, saisi_le: new Date(s.saisi_le).toISOString(), statut: "envoyee" });
    }
  }, []);

  const synchroniser = useCallback(async () => {
    if (enCours.current) return;
    enCours.current = true;
    try {
      const locale = await db.jeu.get("courant");
      if (locale) setEtat((e) => ({ ...e, jeu: locale.donnees, source: locale.source, recuLe: locale.recu_le }));
      let serveur = "injoignable", message = null;
      try {
        const rep = await chercher("/api/donnees");
        const corps = await rep.json().catch(() => ({}));
        if (rep.ok) {
          serveur = "ok";
          const ligne = locale?.version === corps.version && locale?.source === "serveur" ? locale : await enregistrer(corps, "serveur");
          setEtat({ jeu: ligne.donnees, source: "serveur", recuLe: ligne.recu_le, serveur, message: null });
        } else {
          serveur = corps.erreur === "base_non_configuree" ? "sans_base" : "erreur";
          message = corps.message ?? "Le serveur n'a pas pu fournir les données.";
        }
      } catch {
        serveur = "injoignable";
      }
      if (serveur !== "ok") {
        let ligne = locale;
        // The snapshot shipped with the app (kept by the service worker): used when the device has
        // nothing yet, or to replace an older snapshot after an update of the app. Data received from
        // the server are never replaced by a snapshot.
        if (!ligne || ligne.source === "instantane") {
          try {
            const rep = await chercher("/data/tableau_de_bord.json");
            const instantane = rep.ok ? await rep.json() : null;
            if (instantane && instantane.version !== ligne?.version) ligne = await enregistrer(instantane, "instantane");
          } catch { /* handled below: no data at all */ }
        }
        setEtat({ jeu: ligne?.donnees ?? null, source: ligne?.source ?? null, recuLe: ligne?.recu_le ?? null, serveur, message });
      }
      if (serveur === "ok") {
        try {
          await envoyerSaisies();
          await recevoirSaisies();
        } catch { /* entries stay on the device; the screen counts them */ }
      }
      await relireSaisies();
    } finally {
      enCours.current = false;
    }
  }, [enregistrer, envoyerSaisies, recevoirSaisies, relireSaisies]);

  useEffect(() => {
    synchroniser();
    const relancer = () => synchroniser();
    // An app comes back to the front often: check the network then too.
    const auRetour = () => { if (document.visibilityState === "visible") synchroniser(); };
    const horsLigne = () => setEtat((e) => ({ ...e, serveur: e.serveur === "sans_base" ? e.serveur : "injoignable" }));
    window.addEventListener("online", relancer);
    window.addEventListener("offline", horsLigne);
    document.addEventListener("visibilitychange", auRetour);
    const minuterie = setInterval(relancer, 60000);
    return () => {
      window.removeEventListener("online", relancer);
      window.removeEventListener("offline", horsLigne);
      document.removeEventListener("visibilitychange", auRetour);
      clearInterval(minuterie);
    };
  }, [synchroniser]);

  const ajouterSaisie = useCallback(async ({ cle, annee, ecoles_ouvertes }) => {
    const s = { client_id: uuid(), cle, annee, ecoles_ouvertes, saisi_le: new Date().toISOString(), statut: "en_attente" };
    await db.saisies.put(s);
    await relireSaisies();
    // Leaves once the cancel window is over (or at the next synchronisation if the network is down).
    setTimeout(() => synchroniser(), DELAI_ANNULATION_MS + 300);
    return s;
  }, [relireSaisies, synchroniser]);

  // Cancel an entry that has not left the device yet. Returns false if it was already sent.
  const retirerSaisie = useCallback(async (clientId) => {
    const s = await db.saisies.get(clientId);
    if (s?.statut !== "en_attente") return false;
    await db.saisies.delete(clientId);
    await relireSaisies();
    return true;
  }, [relireSaisies]);

  const valeur = useMemo(() => ({ ...etat, saisies, envoi, ajouterSaisie, retirerSaisie, synchroniser }),
    [etat, saisies, envoi, ajouterSaisie, retirerSaisie, synchroniser]);
  return <Contexte.Provider value={valeur}>{children}</Contexte.Provider>;
}

export function useDonnees() {
  const v = useContext(Contexte);
  if (!v) throw new Error("useDonnees hors de DonneesProvider");
  return v;
}

// Latest entry per region for a school year (the one the screens show).
export function derniereSaisie(saisies, cle, annee) {
  return saisies.filter((s) => s.cle === cle && s.annee === annee)
    .sort((a, b) => String(b.saisi_le).localeCompare(String(a.saisi_le)))[0] ?? null;
}
