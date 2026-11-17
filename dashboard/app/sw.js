// Service worker (Serwist): keeps every page, script, style, the data snapshot and the PDF fiches
// on the device. The API is never answered from a cache: the app reads its data from the device
// database and must know when the server does not answer, to say so on screen.
import { defaultCache } from "@serwist/next/worker";
import { NetworkOnly, Serwist } from "serwist";

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  precacheOptions: { ignoreURLParametersMatching: [/.*/] },
  // A new version WAITS: taking over a page while it loads made it ask for scripts of the old
  // version that the new one had just deleted ("Application error ... while loading"). The page
  // tells the worker when it is safe to switch (components/EnregistrementSW.js).
  skipWaiting: false,
  clientsClaim: true,
  navigationPreload: false,
  runtimeCaching: [
    { matcher: ({ url, sameOrigin }) => sameOrigin && url.pathname.startsWith("/api/"), handler: new NetworkOnly() },
    ...defaultCache,
  ],
});

self.addEventListener("message", (e) => {
  if (e.data?.type === "SKIP_WAITING") self.skipWaiting();
});

serwist.addEventListeners();
