import { useEffect, useState } from "react";
import "./Shop.scss";

import ProductCard from "@/components/ProductCard/ProductCard";


interface Product {
  id: number;
  name: string;
  description: string;
  prices: {
    price: string;
    currency_symbol: string;
  };
}


export default function Shop() {

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {

    fetch("http://localhost:8080/wp-json/wc/store/v1/products")

      .then((response) => response.json())

      .then((data) => {

        console.log("WooCommerce products:", data);

        setProducts(data);
        setLoading(false);

      })

      .catch((error) => {

        console.error(
          "WooCommerce API error:",
          error
        );

        setLoading(false);

      });


  }, []);



  if (loading) {

    return (

      <section
        id="shop"
        className="shop"
      >

        <h2>
          Loading products...
        </h2>

      </section>

    );

  }


  console.log("Products state:", products);



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

                id={product.id}

                name={product.name}

                description={
                  product.description
                    .replace(/<[^>]*>/g, "")
                }

                price={
                  `${Number(product.prices.price) / 100} ${product.prices.currency_symbol}`
                }

              />

            )
          )
        }

      </div>


    </section>

  );

}