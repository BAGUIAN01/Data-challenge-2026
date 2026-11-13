"use client";
// Small pieces shared by the pages.
import { useDonnees } from "../DonneesProvider";
import { niveauRisque, PRIORITES } from "@/lib/format";

// Renders the page only once data are on screen; the banner says why when they are not.
export function AvecDonnees({ children }) {
  const { jeu } = useDonnees();
  if (!jeu) return <p className="discret">Les données s'affichent dès qu'elles sont lues sur cet appareil.</p>;
  return children(jeu);
}

export function Tuile({ libelle, valeur, sous }) {
  return (
    <div className="tuile">
      <div className="tuile-libelle">{libelle}</div>
      <div className="tuile-valeur">{valeur}</div>
      {sous && <div className="tuile-sous">{sous}</div>}
    </div>
  );
}

export function BadgePriorite({ p }) {
  return <span className={`badge prio-${p}`}>{PRIORITES[p].libelle}</span>;
}

export function Risque({ p, seuils }) {
  const n = niveauRisque(p, seuils);
  return <span className={`risque ${n.classe}`}>{p} % · {n.libelle}</span>;
}

export function trierRegions(regions) {
  return [...regions].sort((a, b) => a.priorite - b.priorite || a.tap.at(-1) - b.tap.at(-1));
}
