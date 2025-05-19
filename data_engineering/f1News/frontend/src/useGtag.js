// src/useGtag.js
import { useEffect } from "react";
const GA4_ID = "G-VDNHNPPSQX"
function useGtag() {
  useEffect(() => {
    if (!GA4_ID) return;

    const script1 = document.createElement("script");
    script1.async = true;
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`;
    document.head.appendChild(script1);

    const script2 = document.createElement("script");
    script2.innerHTML = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${GA4_ID}');
    `;
    document.head.appendChild(script2);
  }, []);
}

export default useGtag;
