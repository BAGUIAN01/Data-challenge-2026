import "./globals.css";
import { DonneesProvider } from "@/components/DonneesProvider";
import BandeauEtat from "@/components/BandeauEtat";
import Navigation from "@/components/Navigation";
import EnregistrementSW from "@/components/EnregistrementSW";

export const metadata = {
  title: "Décrochage scolaire : anticiper par région",
  description: "Où agir en premier, où le risque monte, combien d'enfants sont en jeu. Fonctionne sans réseau.",
  manifest: "/manifest.webmanifest",
};

export const viewport = { width: "device-width", initialScale: 1, themeColor: "#2a78d6" };

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>
        <DonneesProvider>
          <header className="entete">
            <div className="entete-int">
              <a className="marque" href="/">
                Décrochage scolaire au primaire
                <small>Anticiper le risque par région · Burkina Faso</small>
              </a>
              <Navigation />
            </div>
          </header>
          <BandeauEtat />
          <main className="contenu">{children}</main>
          <footer className="pied">
            Sources : DGESS (données du Data Challenge Burkina 2026) ; ACLED, IGB, Cadre Harmonisé, EDS, CONASUR via HDX ; INSD (EHCVM 2021).
            Calculs de l'équipe. Aucune donnée personnelle.
          </footer>
        </DonneesProvider>
        <EnregistrementSW />
      </body>
    </html>
  );
}
