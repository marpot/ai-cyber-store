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

interface RecommendedProduct {
  id: number;
  name: string;
  price: string;
  category: string;
  description: string;
  image?: string;
}

interface Message {
  id: number;
  role: "ai" | "user";
  content: string;
  products?: RecommendedProduct[];
}

export default function RecommendationBox() {
  const { t, i18n } = useTranslation();

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

  /*
   * Aktualizujemy powitanie początkowe
   * przy zmianie języka strony.
   */
  useEffect(() => {
    setMessages((previous) => {
      if (previous.length === 1 && previous[0].role === "ai") {
        return [
          {
            id: 1,
            role: "ai",
            content: t("recommendations.welcome"),
          },
        ];
      }
      return previous;
    });
  }, [i18n.language, t]);

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
       * z pytaniem użytkownika oraz aktualnym językiem
       */
      const response: RecommendationResponse =
        await getRecommendation(message, i18n.language);

      /*
       * Dodajemy odpowiedź AI wraz z rekomendowanymi produktami do rozmowy
       */
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "ai",
          content: response.message,
          products:
            response.products && response.products.length > 0
              ? response.products
              : undefined,
        },
      ]);
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
                  <div className="recommendations__message-text">
                    {message.content}
                  </div>

                  {message.products && message.products.length > 0 && (
                    <div className="recommendations__chat-products">
                      {message.products.map((product) => (
                        <div
                          key={product.id}
                          className="recommendations__chat-product"
                        >
                          <div className="recommendations__chat-product-header">
                            <span className="recommendations__chat-product-icon">🛡️</span>
                            <h4 className="recommendations__chat-product-title">
                              {product.name}
                            </h4>
                            <span className="recommendations__chat-product-price">
                              {product.price}
                            </span>
                          </div>

                          <p className="recommendations__chat-product-desc">
                            {product.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
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

    </section>
  );
}