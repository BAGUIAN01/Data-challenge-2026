"use client";
// Width of a container in CSS pixels. Charts draw with one SVG unit = one pixel, so their text keeps
// its real size on a phone instead of shrinking with the drawing.
import { useEffect, useState } from "react";

export default function useLargeur(ref, defaut = 640) {
  const [largeur, setLargeur] = useState(defaut);
  useEffect(() => {
    // The element is captured here: a resize callback may still arrive after the screen has gone.
    const el = ref.current;
    if (!el) return undefined;
    const mesurer = () => {
      const w = Math.round(el.getBoundingClientRect().width);
      if (w > 0) setLargeur(Math.max(240, w)); // a hidden tab measures 0: keep the last width
    };
    mesurer();
    const ro = new ResizeObserver(mesurer);
    ro.observe(el);
    return () => ro.disconnect();
  }, [ref]);
  return largeur;
}
