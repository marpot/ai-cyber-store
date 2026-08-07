import i18n from "i18next";

import {
  initReactI18next
} from "react-i18next";

import en from "./locales/en.json";
import pl from "./locales/pl.json";


i18n
  .use(initReactI18next)
  .init({

    resources: {

      en: {
        translation: en,
      },

      pl: {
        translation: pl,
      }

    },


    lng: localStorage.getItem("language") || "pl",

    fallbackLng: "en",


    interpolation: {
      escapeValue: false,
    }

  });


export default i18n;