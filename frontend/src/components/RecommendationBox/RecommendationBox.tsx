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
  return (
    <section className="recommendations">

      <div className="recommendations__header">

        <h2>
          AI Recommended Products
        </h2>

        <p>
          Security tools selected by our intelligent recommendation engine.
        </p>

      </div>


      <div className="recommendations__grid">

        {products.map((product) => (
          <ProductCard
            key={product.id}
            name={product.name}
            description={product.description}
            price={product.price}
          />
        ))}

      </div>

    </section>
  );
}