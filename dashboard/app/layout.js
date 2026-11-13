import "./globals.css";
import { DonneesProvider } from "@/components/DonneesProvider";
import EnregistrementSW from "@/components/EnregistrementSW";

export const metadata = {
  title: "Décrochage scolaire : anticiper par région",
  description: "Où agir en premier, où le risque monte, combien d'élèves sont en jeu, région par région. Fonctionne sans réseau.",
  manifest: "/manifest.webmanifest",
  applicationName: "Décrochage",
  appleWebApp: { capable: true, title: "Décrochage", statusBarStyle: "default" },
  icons: { icon: "/icone.svg", apple: "/icone-180.png" },
  formatDetection: { telephone: false },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f2f3f6" },
    { media: "(prefers-color-scheme: dark)", color: "#07090d" },
  ],
};

// Applies the theme chosen on this device before the first paint (no flash of the other theme).
const THEME = `try{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: THEME }} /></head>
      <body>
        <DonneesProvider>{children}</DonneesProvider>
        <EnregistrementSW />
      </body>
    </html>
  );
}
