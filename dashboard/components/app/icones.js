// Line icons (24 px grid) and the app's logo. Icons always come with a written label next to them.

const trace = { className: "i", viewBox: "0 0 24 24", "aria-hidden": true };

export const Chevron = () => <svg {...trace} className="i chev"><path d="m9 18 6-6-6-6" /></svg>;
export const Retour = () => <svg {...trace}><path d="m15 18-6-6 6-6" /></svg>;
export const IcCarte = () => <svg {...trace}><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z" /><path d="M9 4v14M15 6v14" /></svg>;
export const IcRegions = () => <svg {...trace}><path d="M8 6h12M8 12h12M8 18h12" /><path d="M4 6h.01M4 12h.01M4 18h.01" strokeWidth="2.6" /></svg>;
export const IcAlertes = () => <svg {...trace}><path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z" /><path d="M10 20.5a2 2 0 0 0 4 0" /></svg>;
export const IcPlus = () => <svg {...trace}><path d="M4 7h16M4 12h16M4 17h16" /></svg>;

// The app icon, kept on the device by the service worker like every public file.
export function IconeApp() {
  return <img className="appi" src="/icone-192.png" alt="" width="192" height="192" />;
}
