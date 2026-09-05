import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import ru from "@/locales/ru.json";
import kk from "@/locales/kk.json";
import en from "@/locales/en.json";

const resources = {
  ru: { translation: ru },
  kk: { translation: kk },
  en: { translation: en },
};

const STORAGE_KEY = "bailanysta_lang";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "ru",
    supportedLngs: ["ru", "kk", "en"],
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: STORAGE_KEY,
      caches: ["localStorage"],
    },
    interpolation: {
      escapeValue: false,
    },
  });

i18n.on("languageChanged", (lng) => {
  try {
    localStorage.setItem(STORAGE_KEY, lng);
    document.documentElement.lang = lng;
  } catch {
    // ignore
  }
});

// set initial html lang
if (typeof document !== "undefined") {
  document.documentElement.lang = i18n.language?.split("-")[0] ?? "ru";
}

export default i18n;
export { STORAGE_KEY };
