"use client";
// Plain links (full page loads): every page is kept by the service worker, so navigation works
// without network; client-side transitions would need server payloads that may not be cached.
import { usePathname } from "next/navigation";

const LIENS = [
  ["/", "Carte"],
  ["/priorites", "Priorités"],
  ["/alertes", "Alertes et saisie"],
  ["/methode", "Méthode"],
];

export default function Navigation() {
  const chemin = usePathname();
  return (
    <nav className="nav" aria-label="Pages du tableau de bord">
      {LIENS.map(([href, libelle]) => (
        <a key={href} href={href} aria-current={(href === "/" ? chemin === "/" || chemin.startsWith("/region") : chemin.startsWith(href)) ? "page" : undefined}>
          {libelle}
        </a>
      ))}
    </nav>
  );
}
