"use client";
// Says where the data on screen come from, and what to do when something cannot happen.
import { useDonnees } from "./DonneesProvider";
import { dateFr, dateHeureFr } from "@/lib/format";

export default function BandeauEtat() {
  const { jeu, source, recuLe, serveur, message, saisies } = useDonnees();
  const attente = saisies.filter((s) => s.statut === "en_attente").length;
  let ton = "info", texte;
  if (!jeu && serveur === "inconnu") texte = "Lecture des données de cet appareil…";
  else if (!jeu) {
    ton = "alerte";
    texte = "Aucune donnée sur cet appareil et pas de réseau. Ouvrez l'application une première fois avec une connexion : elle fonctionnera ensuite sans réseau.";
  } else if (source === "serveur" && serveur === "ok") {
    texte = `Données à jour (version du ${dateFr(jeu.genere_le)}), enregistrées sur cet appareil.`;
  } else if (serveur === "injoignable") {
    ton = "hors-ligne";
    texte = `Sans réseau : données de cet appareil, reçues le ${dateHeureFr(recuLe)} (version du ${dateFr(jeu.genere_le)}). Elles se mettront à jour au retour du réseau.`;
  } else {
    texte = `Données publiées avec l'application (version du ${dateFr(jeu.genere_le)}). ${message ?? ""}`.trim();
  }
  return (
    <div className={`bandeau bandeau-${ton}`} role="status">
      <span>{texte}</span>
      {attente > 0 && (
        <span className="bandeau-attente">
          {attente === 1 ? "1 saisie attend" : `${attente} saisies attendent`} le réseau pour partir. Rien n'est perdu.
        </span>
      )}
    </div>
  );
}
