import Application from "@/components/app/Application";

// The whole app is one page: kept by the service worker, it opens without network; screens are
// navigated inside it (history entries, #region/X addresses).
export default function Page() {
  return <Application />;
}
