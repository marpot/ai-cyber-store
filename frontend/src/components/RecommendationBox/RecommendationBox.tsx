import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import ProductCard from "@/components/ProductCard/ProductCard";

import "./RecommendationBox.scss";

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

export default function RecommendationBox() {
  const { t } = useTranslation();

  const API_URL = import.meta.env.VITE_WP_API_URL;

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/wp-json/wc/store/v1/products`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `WooCommerce HTTP ${response.status}`
          );
        }

        return response.json();
      })
      .then((data: Product[]) => {
        console.log("WooCommerce recommendations:", data);

        setProducts(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(
          "WooCommerce recommendations error:",
          error
        );

        setLoading(false);
      });
  }, [API_URL]);

  if (loading) {
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
      </section>
    );
  }

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
        {products.map((product) => (
          <ProductCard
            key={product.id}
            id={product.id}
            name={product.name}
            description={product.description.replace(
              /<[^>]*>/g,
              ""
            )}
            price={`${Number(product.prices.price) / 100} ${
              product.prices.currency_symbol
            }`}
            image={product.images?.[0]?.src}
            isOnSale={product.is_on_sale}
          />
        ))}
      </div>
    </section>
  );
}