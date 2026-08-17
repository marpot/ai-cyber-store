import { useTranslation } from "react-i18next";

import "@/components/LanguageSwitcher/LanguageSwitcher.scss";


export default function LanguageSwitcher() {


  const {
    i18n
  } = useTranslation();



  const changeLanguage = (language: string) => {

    i18n.changeLanguage(language);

    localStorage.setItem(
      "language",
      language
    );

  };



  return (

    <div className="language-switcher">


      <button
        className={
          i18n.language === "pl"
            ? "active"
            : ""
        }
        onClick={() => changeLanguage("pl")}
      >
        PL
      </button>



      <button
        className={
          i18n.language === "en"
            ? "active"
            : ""
        }
        onClick={() => changeLanguage("en")}
      >
        EN
      </button>


    </div>

  );

}