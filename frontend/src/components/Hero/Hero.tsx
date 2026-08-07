import { useTranslation } from "react-i18next";

import "./Hero.scss";


export default function Hero() {


  const {
    t
  } = useTranslation();



  return (

    <section
      id="home"
      className="hero"
    >

      <div className="hero__content">


        <h1>
          {t("hero.title")}
        </h1>


        <h2>
          {t("hero.subtitle")}
        </h2>


        <p>
          {t("hero.description")}
        </p>


        <button>
          {t("hero.button")}
        </button>


      </div>

    </section>

  );

}