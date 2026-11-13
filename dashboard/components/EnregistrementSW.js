"use client";
// Registers the service worker that keeps every page, the scripts and the data snapshot on the
// device. Only in production builds (the worker is not generated in development).
import { useEffect } from "react";

export default function EnregistrementSW() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production" || !("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch((e) => console.error("service worker", e));
  }, []);
  return null;
}
