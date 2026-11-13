// One static page per region, built from the exported data: no server reading at request time,
// so the page can be kept by the service worker and opened without network.
import { readFileSync } from "node:fs";
import path from "node:path";
import PageRegion from "@/components/pages/PageRegion";

export const dynamicParams = false;

function jeu() {
  return JSON.parse(readFileSync(path.join(process.cwd(), "public/data/tableau_de_bord.json"), "utf8"));
}

export function generateStaticParams() {
  return jeu().regions.map((r) => ({ cle: r.cle }));
}

export async function generateMetadata({ params }) {
  const { cle } = await params;
  const r = jeu().regions.find((x) => x.cle === cle);
  return { title: r ? `${r.nom} : fiche régionale` : "Région" };
}

export default async function Page({ params }) {
  const { cle } = await params;
  return <PageRegion cle={cle} />;
}
