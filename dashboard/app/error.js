"use client";
import { useEffect } from "react";
import Reprise from "@/components/app/Reprise";

export default function Erreur({ error, reset }) {
  useEffect(() => { console.error(error); }, [error]);
  return <Reprise reset={reset} />;
}
