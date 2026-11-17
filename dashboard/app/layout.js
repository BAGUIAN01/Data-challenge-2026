import "./globals.css";
import { DonneesProvider } from "@/components/DonneesProvider";
import EnregistrementSW from "@/components/EnregistrementSW";

export const metadata = {
  title: "Décrochage scolaire : anticiper par région",
  description: "Où agir en premier, où le risque monte, combien d'élèves sont en jeu, région par région. Fonctionne sans réseau.",
  manifest: "/manifest.webmanifest",
  applicationName: "Décrochage",
  appleWebApp: { capable: true, title: "Décrochage", statusBarStyle: "default" },
  icons: { icon: [{ url: "/favicon-32.png", sizes: "32x32" }, { url: "/icone-192.png", sizes: "192x192" }], apple: "/icone-180.png" },
  formatDetection: { telephone: false },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#f2f3f6", // light by default, whatever the phone's setting
};

// Safety net: if Next's bare "Application error" page shows anyway (a script that could not load
// while loading), reload once by itself instead of leaving the user on it. At most once a minute.
const SECOURS = `(function(){var prevu=0;function v(){prevu=0;var h=document.querySelectorAll("h2"),i,ok=0;for(i=0;i<h.length;i++)if(/Application error: a client-side exception/.test(h[i].textContent||""))ok=1;if(!ok)return;try{var t=+sessionStorage.getItem("secours")||0;if(Date.now()-t<60000)return;sessionStorage.setItem("secours",String(Date.now()))}catch(e){return}location.reload()}new MutationObserver(function(){if(!prevu)prevu=setTimeout(v,1000)}).observe(document.documentElement,{childList:true,subtree:true})})()`;

// Applies the theme chosen on this device before the first paint (no flash of the other theme).
const THEME = `try{var t=localStorage.getItem("theme");if(t==="dark"||t==="auto")document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: THEME }} /><script dangerouslySetInnerHTML={{ __html: SECOURS }} /></head>
      <body>
        <DonneesProvider>{children}</DonneesProvider>
        <EnregistrementSW />
      </body>
    </html>
  );
}
