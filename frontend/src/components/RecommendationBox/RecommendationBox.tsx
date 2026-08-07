import { useTranslation } from "react-i18next";

import ProductCard from "@/components/ProductCard/ProductCard";

import "./RecommendationBox.scss";


const products = [
  {
    id: 1,
    name: "AI Threat Scanner",
    description:
      "AI powered vulnerability analysis system.",
    price: "$199",
  },
  {
    id: 2,
    name: "Secure VPN Pro",
    description:
      "Advanced privacy and network protection.",
    price: "$49",
  },
  {
    id: 3,
    name: "Password Guardian AI",
    description:
      "Smart password security assistant.",
    price: "$29",
  },
];


export default function RecommendationBox() {


  const {
    t
  } = useTranslation();



  return (

    <section
      id="recommendations"
      className="recommendations"
    >


      <div className="recommendations__header">


        <h2>
          {t("recommendations.title")}
        </h2>


        <p>
          {t("recommendations.description")}
        </p>


      </div>



      <div className="recommendations__grid">


        {
          products.map(
            (product) => (

              <ProductCard

                key={product.id}

                id={product.id}

                name={product.name}

                description={product.description}

                price={product.price}

              />

            )
          )
        }


      </div>


    </section>

  );

}