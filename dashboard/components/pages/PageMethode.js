"use client";
import { AvecDonnees } from "./communs";
import { useDonnees } from "../DonneesProvider";
import { dateFr, dateHeureFr, fr } from "@/lib/format";

export default function PageMethode() {
  const { source, recuLe, serveur } = useDonnees();
  return (
    <AvecDonnees>
      {(jeu) => {
        const v = jeu.validation;
        return (
          <>
            <h1>Méthode et limites</h1>
            <p className="sous-titre">Ce que l'outil sait faire, avec quelle fiabilité, et ce qu'il ne sait pas faire.</p>
            <section className="carte-bloc">
              <h2>Ce qui a été vérifié, sur des années que les modèles n'avaient pas vues</h2>
              <ul className="puces">
                <li><strong>Où sera le risque l'an prochain :</strong> le classement des régions par taux d'achèvement se retrouve d'une année à l'autre
                  (corrélation de rang {fr(v.rang_tap, 2)}).</li>
                <li><strong>Où le risque monte :</strong> la violence annonce les fortes baisses d'effectifs (AUC {fr(v.auc_reference, 2)} ;
                  {" "}{fr(v.auc_septembre, 2)} fin septembre ; {fr(v.auc_janvier, 2)} début janvier).</li>
                <li><strong>Combien d'élèves :</strong> avec le nombre d'écoles ouvertes à la rentrée, l'erreur sur les effectifs tombe à
                  {" "}± {fr(jeu.nowcast.erreur_pct, 1)} %, contre ± {fr(jeu.nowcast.erreur_persistance_pct, 1)} % sans.</li>
                <li><strong>La matrice de priorité,</strong> rejouée sur le passé : {v.matrice_regions_pct} % des régions, {v.matrice_baisses_pct} % des fortes baisses.</li>
              </ul>
            </section>
            <section className="carte-bloc">
              <h2>Ce que l'outil ne sait pas faire</h2>
              <ul className="puces">
                <li>Prévoir à l'aveugle de combien le taux d'achèvement va bouger : aucun modèle testé ne bat « comme l'an passé ».</li>
                <li>Voir les réouvertures d'écoles : ce sont des décisions de l'État, absentes des données.</li>
                <li>Descendre aux provinces ou aux 17 nouvelles régions : les données du challenge sont publiées sur les 13 anciennes.</li>
                <li>Mesurer directement l'abandon : il n'y a ni redoublants ni abandons dans les données ; on utilise des substituts.</li>
                <li>Mesurer l'orpaillage, le mariage précoce, la distance à l'école : aucune série publique par région.</li>
              </ul>
            </section>
            <section className="carte-bloc">
              <h2>Fonctionnement sans réseau</h2>
              <p>
                Les données sont enregistrées sur cet appareil. Les pages, la carte et les fiches PDF sont gardées par l'application : tout s'ouvre
                sans réseau après une première visite. Les saisies sont gardées sur l'appareil et partent vers la base en ligne (Neon) au retour du réseau,
                sans être perdues ni comptées deux fois.
              </p>
              <p className="discret">
                Version des données : {jeu.version}, du {dateFr(jeu.genere_le)} · source sur cet appareil : {
                  source === "serveur" ? "base en ligne" : source === "instantane" ? "données publiées avec l'application" : "—"}
                {" "}· reçue le {dateHeureFr(recuLe)} · base en ligne : {serveur === "ok" ? "jointe" : serveur === "sans_base" ? "non configurée" : "injoignable"}.
              </p>
            </section>
          </>
        );
      }}
    </AvecDonnees>
  );
}
