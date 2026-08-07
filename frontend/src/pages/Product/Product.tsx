import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import "./Product.scss";


export default function Product() {

  const { id } = useParams();

  const { t } = useTranslation();


  return (

    <section className="product-page">


      <Link
        to="/"
        className="product-page__back"
      >
        ← {t("product.back")}
      </Link>



      <div className="product-page__content">

        <h1>
          {t("product.title")}
        </h1>


        <p>
          ID: {id}
        </p>


      </div>


    </section>

  );

}