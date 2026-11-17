"use client";
// Shown instead of a blank "Application error" page when a screen crashes. The button drops the
// data copy kept on the device (the likely cause) and reloads; field entries are kept.
import { useEffect, useState } from "react";
import { db } from "@/lib/db-locale";

// A script of another version that could not be loaded: a plain reload fixes it, so do it once
// by itself (at most once a minute) instead of asking.
const SCRIPT_ABSENT = /ChunkLoadError|Loading (CSS )?chunk|dynamically imported module|Importing a module script failed/i;

export default function Reprise({ reset, error }) {
  const [enCours, setEnCours] = useState(false);
  useEffect(() => {
    if (!SCRIPT_ABSENT.test(`${error?.name} ${error?.message}`)) return;
    try {
      const t = Number(sessionStorage.getItem("secours")) || 0;
      if (Date.now() - t < 60000) return;
      sessionStorage.setItem("secours", String(Date.now()));
    } catch { return; }
    window.location.reload();
  }, [error]);
  const reprendre = async () => {
    setEnCours(true);
    try { await db.jeu.delete("courant"); } catch { /* storage refused: reload anyway */ }
    window.location.reload();
  };
  return (
    <div className="lancement" role="alert" style={{ maxWidth: 360, margin: "0 auto" }}>
      <b>Décrochage scolaire</b>
      <p>Un écran n'a pas pu s'afficher. Vos saisies sont gardées sur ce téléphone.</p>
      <button type="button" className="btn" onClick={reprendre} disabled={enCours}>
        {enCours ? "Rechargement…" : "Recharger les données"}
      </button>
      {reset ? <button type="button" className="btn2" onClick={() => reset()}>Réessayer sans recharger</button> : null}
    </div>
  );
}
