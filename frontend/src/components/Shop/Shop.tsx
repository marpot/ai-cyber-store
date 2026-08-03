import "./Shop.scss";

import ProductCard from "@/components/ProductCard/ProductCard";


const products = [
  {
    id: 1,
    name: "AI Security Scanner",
    description: "AI powered vulnerability scanner",
    price: "$49",
  },

  {
    id: 2,
    name: "Cyber Monitor Pro",
    description: "Advanced threat monitoring system",
    price: "$99",
  },

  {
    id: 3,
    name: "Network Guardian",
    description: "AI network protection tool",
    price: "$149",
  },
];


export default function Shop() {

  return (

    <section
      id="shop"
      className="shop"
    >

      <div className="shop__header">

        <h2>
          Shop
        </h2>


        <p>
          Explore AI cybersecurity solutions
        </p>

      </div>



      <div className="shop__grid">

        {
          products.map(
            (product) => (

              <ProductCard

                key={product.id}

                id = {product.id}

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