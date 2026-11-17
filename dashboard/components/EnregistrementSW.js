"use client";
// Registers the service worker that keeps every page, the scripts and the data snapshot on the
// device. Only in production builds (the worker is not generated in development).
// Updates: a new version waits (see app/sw.js) and is switched on at a safe moment only, then the
// page reloads once so that page and scripts come from the same version:
//   - right after opening (nothing in progress yet), or
//   - when the app goes to the background (the user does not see the reload).
import { useEffect } from "react";

const OUVERTURE_MS = 10000;

export default function EnregistrementSW() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production" || !("serviceWorker" in navigator)) return;
    const debut = Date.now();
    // First visit: the worker takes control without any version change, so no reload then.
    const dejaInstalle = !!navigator.serviceWorker.controller;
    let reg = null, recharge = false;

    const basculer = () => {
      const enAttente = reg?.waiting;
      if (!enAttente || !navigator.serviceWorker.controller) return;
      if (Date.now() - debut < OUVERTURE_MS || document.visibilityState === "hidden") {
        enAttente.postMessage({ type: "SKIP_WAITING" });
      }
    };
    const surChangement = () => {
      if (recharge || !dejaInstalle) return;
      recharge = true;
      window.location.reload();
    };
    const surVisibilite = () => { if (document.visibilityState === "hidden") basculer(); };

    navigator.serviceWorker.addEventListener("controllerchange", surChangement);
    document.addEventListener("visibilitychange", surVisibilite);
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).then((r) => {
      reg = r;
      basculer();
      r.addEventListener("updatefound", () => {
        const nouveau = r.installing;
        nouveau?.addEventListener("statechange", () => { if (nouveau.state === "installed") basculer(); });
      });
    }).catch((e) => console.error("service worker", e));
    return () => {
      navigator.serviceWorker.removeEventListener("controllerchange", surChangement);
      document.removeEventListener("visibilitychange", surVisibilite);
    };
  }, []);
  return null;
}
