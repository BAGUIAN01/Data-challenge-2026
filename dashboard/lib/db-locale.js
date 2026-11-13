// The device database (IndexedDB through Dexie): the dashboard reads from here first, always.
import Dexie from "dexie";

export const db = new Dexie("tableau-de-bord-decrochage");
db.version(1).stores({
  jeu: "cle",                          // one row, cle = "courant": { donnees, version, source, recu_le }
  saisies: "client_id, cle, statut",   // field entries; statut = en_attente | envoyee
});
