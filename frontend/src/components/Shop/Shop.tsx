import { useEffect, useState } from "react";
import "./Shop.scss";

import ProductCard from "@/components/ProductCard/ProductCard";

import { useTranslation } from "react-i18next";


interface Product {
  id: number;

  name: string;

  description: string;

  prices: {
    price: string;
    currency_symbol: string;
  };

  images: {
    src: string;
    alt: string;
  }[];

  is_on_sale: boolean;
}


export default function Shop() {


  const { t } = useTranslation();


  const API_URL =
    import.meta.env.VITE_WP_API_URL || "http://localhost:8080";


  const [products, setProducts] = useState<Product[]>([]);

  const [loading, setLoading] = useState(true);



  useEffect(() => {


    fetch(`${API_URL}/wp-json/wc/store/v1/products`)


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


  }, [API_URL]);




  if (loading) {


    return (

      <section
        id="shop"
        className="shop"
      >

        <h2>
          {t("shop.loading")}
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
          {t("shop.title")}
        </h2>



        <p>
          {t("shop.description")}
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


                image={
                  product.images?.[0]?.src
                }


                isOnSale={
                  product.is_on_sale
                }


              />


            )

          )

        }


      </div>


    </section>


  );


}