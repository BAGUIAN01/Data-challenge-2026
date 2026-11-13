import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import withSerwistInit from "@serwist/next";

// Pages to keep on the device at install time. The revision changes at every build, so that a new
// build replaces the pages (their scripts change names from one build to the next).
const jeu = JSON.parse(readFileSync(new URL("./public/data/tableau_de_bord.json", import.meta.url), "utf8"));
const pages = ["/", "/priorites", "/alertes", "/methode", ...jeu.regions.map((r) => `/region/${r.cle}`)];
const revision = `${jeu.version}-${Date.now()}`;

// Files of public/ (data snapshot, PDF fiches, icon, manifest). Serwist stops scanning public/ as
// soon as additionalPrecacheEntries is given, so they are listed here, revision = content hash.
const PUBLIC = path.join(path.dirname(new URL(import.meta.url).pathname), "public");
const publics = readdirSync(PUBLIC, { recursive: true, withFileTypes: true })
  .filter((d) => d.isFile() && !/^(sw\.js(\.map)?|swe-worker-.*\.js)$/.test(d.name))
  .map((d) => {
    const complet = path.join(d.parentPath ?? d.path, d.name);
    return { url: "/" + path.relative(PUBLIC, complet).split(path.sep).join("/"),
      revision: createHash("md5").update(readFileSync(complet)).digest("hex") };
  });

const withSerwist = withSerwistInit({
  swSrc: "app/sw.js",
  swDest: "public/sw.js",
  register: false, // registered by components/EnregistrementSW.js
  additionalPrecacheEntries: [...pages.map((url) => ({ url, revision })), ...publics],
  disable: process.env.NODE_ENV === "development",
});

export default withSerwist({ reactStrictMode: true, poweredByHeader: false });
