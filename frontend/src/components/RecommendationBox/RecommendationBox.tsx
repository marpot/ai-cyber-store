import {
  FormEvent,
  useState,
} from "react";

import { useTranslation } from "react-i18next";

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
  image?: string;
}

export default function RecommendationBox() {
  const { t } = useTranslation();

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

    /*
     * MOCK
     *
     * Tymczasowo symulujemy odpowiedź AI.
     *
     * W kolejnym kroku zastąpimy ten fragment
     * requestem do FastAPI.
     */

    setTimeout(() => {
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "ai",
          content: t(
            "recommendations.mockResponse"
          ),
        },
      ]);

      setLoading(false);
    }, 1000);
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

                  <div>
                    <h4>
                      {product.name}
                    </h4>

                    <span>
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