"use client";
// Last resort when the root layout itself fails: it replaces <html>, so it brings its own styles.
import { useEffect } from "react";
import "./globals.css";
import Reprise from "@/components/app/Reprise";

export default function ErreurGlobale({ error }) {
  useEffect(() => { console.error(error); }, [error]);
  return (
    <html lang="fr">
      <body><Reprise error={error} /></body>
    </html>
  );
}
