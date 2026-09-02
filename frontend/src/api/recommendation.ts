export interface RecommendationResponse {
  intent: string;
  confidence: number;
  message: string;
  products: {
    id: number;
    name: string;
    price: string;
    category: string;
    description: string;
  }[];
}

/**
 * Get AI recommendation based on user message
 * Sends message to backend, gets intent classification
 * and product recommendations based on the intent
 */
export async function getRecommendation(
  message: string,
  language: string = "pl"
): Promise<RecommendationResponse> {
  try {
    const response = await fetch("/api/recommendation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, language }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get recommendation:", error);
    throw error;
  }
}

/**
 * Check if recommendation service is available
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch("/health", {
      method: "GET",
    });
    return response.ok;
  } catch (error) {
    console.error("Recommendation service is unavailable:", error);
    return false;
  }
}
