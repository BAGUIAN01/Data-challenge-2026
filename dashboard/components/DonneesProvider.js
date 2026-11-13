"use client";
// Local-first data layer. Order of reading, always:
//   1. the device database (instant, works without network);
//   2. the server (Neon) when it answers: the device copy is replaced if the version changed;
//   3. the snapshot shipped with the app, only if the device has nothing yet.
// Field entries go to the device first (outbox) and leave when the server answers.
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { db } from "@/lib/db-locale";

const Contexte = createContext(null);
const DELAI_MS = 8000;

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
  const enCours = useRef(false);

  const relireSaisies = useCallback(async () => setSaisies(await db.saisies.toArray()), []);

  const enregistrer = useCallback(async (donnees, source) => {
    const ligne = { cle: "courant", donnees, version: donnees.version, source, recu_le: new Date().toISOString() };
    await db.jeu.put(ligne);
    return ligne;
  }, []);

  const envoyerSaisies = useCallback(async () => {
    const attente = await db.saisies.where("statut").equals("en_attente").toArray();
    if (!attente.length) return { envoyees: 0 };
    const rep = await chercher("/api/saisies", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ saisies: attente.map(({ statut, ...s }) => s) }),
    });
    const corps = await rep.json().catch(() => ({}));
    if (!rep.ok) throw Object.assign(new Error(corps.message || "Envoi impossible"), { corps });
    await db.saisies.where("client_id").anyOf(corps.recues ?? []).modify({ statut: "envoyee" });
    return { envoyees: corps.recues?.length ?? 0 };
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
    window.addEventListener("online", relancer);
    const minuterie = setInterval(relancer, 60000);
    return () => {
      window.removeEventListener("online", relancer);
      clearInterval(minuterie);
    };
  }, [synchroniser]);

  const ajouterSaisie = useCallback(async ({ cle, annee, ecoles_ouvertes }) => {
    const s = { client_id: uuid(), cle, annee, ecoles_ouvertes, saisi_le: new Date().toISOString(), statut: "en_attente" };
    await db.saisies.put(s);
    await relireSaisies();
    try {
      await envoyerSaisies();
      setEtat((e) => ({ ...e, serveur: "ok" }));
    } catch { /* stays in the outbox */ }
    await relireSaisies();
    return s;
  }, [envoyerSaisies, relireSaisies]);

  const valeur = useMemo(() => ({ ...etat, saisies, ajouterSaisie, synchroniser }), [etat, saisies, ajouterSaisie, synchroniser]);
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
