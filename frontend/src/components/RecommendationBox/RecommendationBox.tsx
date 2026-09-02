import {
  useEffect,
  useRef,
  useState,
} from "react";
import type { FormEvent } from "react";

import { useTranslation } from "react-i18next";

import { getRecommendation } from "../../api/recommendation.ts";
import type { RecommendationResponse } from "../../api/recommendation.ts";

import "./RecommendationBox.scss";

interface Message {
  id: number;
  role: "ai" | "user";
  content: string;
}

interface RecommendedProduct {
  id: number;
  name: string;
  price: string;
  category: string;
  description: string;
  image?: string;
}

export default function RecommendationBox() {
  const { t } = useTranslation();

  const chatEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "ai",
      content: t(
        "recommendations.welcome"
      ),
    },
  ]);

  const [input, setInput] = useState("");

  const [loading, setLoading] =
    useState(false);

  const [products, setProducts] =
    useState<RecommendedProduct[]>([]);

  /*
   * Automatycznie przewijamy chat
   * do ostatniej wiadomości po każdej
   * zmianie historii wiadomości.
   */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    const message =
      input.trim();

    if (!message || loading) {
      return;
    }

    /*
     * Dodajemy wiadomość użytkownika
     * do historii rozmowy.
     */

    setMessages((previous) => [
      ...previous,
      {
        id: Date.now(),
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      /*
       * Wysyłamy żądanie do FastAPI
       * z pytaniem użytkownika
       */
      const response: RecommendationResponse =
        await getRecommendation(message);

      /*
       * Dodajemy odpowiedź AI do rozmowy
       */
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "ai",
          content: response.message,
        },
      ]);

      /*
       * Aktualizujemy listę rekomendowanych produktów
       */
      if (response.products && response.products.length > 0) {
        setProducts(response.products);
      }
    } catch (error) {
      console.error("Error getting recommendation:", error);

      /*
       * Wyświetlamy komunikat o błędzie
       */
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "ai",
          content: t("recommendations.error") ||
            "Sorry, I couldn't process your request. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      id="recommendations"
      className="recommendations"
    >
      <div className="recommendations__header">

        <h2>
          {t(
            "recommendations.title"
          )}
        </h2>

        <p>
          {t(
            "recommendations.description"
          )}
        </p>

      </div>

      <div className="recommendations__assistant">

        <div className="recommendations__assistant-header">

          <div className="recommendations__status">
            <span />
            AI ONLINE
          </div>

          <span className="recommendations__assistant-label">
            AI SECURITY ASSISTANT
          </span>

        </div>

        <div className="recommendations__chat">

          {messages.map(
            (message) => (
              <div
                key={message.id}
                className={`recommendations__message recommendations__message--${message.role}`}
              >
                <div className="recommendations__message-label">
                  {message.role === "ai"
                    ? "AI"
                    : "YOU"}
                </div>

                <div className="recommendations__message-content">
                  {message.content}
                </div>
              </div>
            )
          )}

          {loading && (
            <div className="recommendations__message recommendations__message--ai">

              <div className="recommendations__message-label">
                AI
              </div>

              <div className="recommendations__typing">
                <span />
                <span />
                <span />
              </div>

            </div>
          )}

          {/* Punkt docelowy automatycznego scrollowania */}
          <div ref={chatEndRef} />

        </div>

        <form
          className="recommendations__input"
          onSubmit={handleSubmit}
        >

          <input
            type="text"
            value={input}
            onChange={(event) =>
              setInput(
                event.target.value
              )
            }
            placeholder={t(
              "recommendations.placeholder"
            )}
            disabled={loading}
          />

          <button
            type="submit"
            disabled={
              loading ||
              !input.trim()
            }
          >
            ➤
          </button>

        </form>

      </div>

      {products.length > 0 && (
        <div className="recommendations__products">

          <h3>
            {t(
              "recommendations.products"
            )}
          </h3>

          <div className="recommendations__products-grid">

            {products.map(
              (product) => (
                <article
                  key={product.id}
                  className="recommendations__product"
                >

                  {product.image && (
                    <img
                      src={
                        product.image
                      }
                      alt={
                        product.name
                      }
                    />
                  )}

                  <div className="recommendations__product-info">
                    <h4>
                      {product.name}
                    </h4>

                    <p className="recommendations__product-description">
                      {product.description}
                    </p>

                    <span className="recommendations__product-price">
                      {product.price}
                    </span>
                  </div>

                </article>
              )
            )}

          </div>

        </div>
      )}

    </section>
  );
}