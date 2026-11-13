"use client";
// Width of a container in CSS pixels. Charts draw with one SVG unit = one pixel, so their text keeps
// its real size on a phone instead of shrinking with the drawing.
import { useEffect, useState } from "react";

export default function useLargeur(ref, defaut = 640) {
  const [largeur, setLargeur] = useState(defaut);
  useEffect(() => {
    if (!ref.current) return;
    const mesurer = () => setLargeur(Math.max(280, Math.round(ref.current.getBoundingClientRect().width)));
    mesurer();
    const ro = new ResizeObserver(mesurer);
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, [ref]);
  return largeur;
}
