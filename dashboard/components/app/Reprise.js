"use client";
// Shown instead of a blank "Application error" page when a screen crashes. The button drops the
// data copy kept on the device (the likely cause) and reloads; field entries are kept.
import { useState } from "react";
import { db } from "@/lib/db-locale";

export default function Reprise({ reset }) {
  const [enCours, setEnCours] = useState(false);
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
