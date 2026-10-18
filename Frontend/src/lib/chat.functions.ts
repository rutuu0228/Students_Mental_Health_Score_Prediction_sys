import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import {
  buildInsights,
  lifestyleCards,
  prettyFeature,
  type AssessmentInput,
} from "./mb";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

type Row = Record<string, unknown>;

function toMessage(row: Row): ChatMessage {
  return {
    id: row["id"] as string,
    role: row["role"] as "user" | "assistant",
    content: row["message"] as string,
    created_at: row["created_at"] as string,
  };
}

export const getChatMessages = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }): Promise<ChatMessage[]> => {
    const { data, error } = await context.supabase
      .from("chat_messages")
      .select("*")
      .eq("user_id", context.userId)
      .order("created_at", { ascending: true })
      .limit(200);

    if (error) {
      throw new Error(
        `Could not load chat history: ${error.message}`
      );
    }

    return (data ?? []).map((row) => toMessage(row as Row));
  });

export const clearChat = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { error } = await context.supabase
      .from("chat_messages")
      .delete()
      .eq("user_id", context.userId);

    if (error) {
      throw new Error(
        `Could not clear chat: ${error.message}`
      );
    }

    return { ok: true };
  });

function buildContext(
  assessment: AssessmentInput | null,
  result: Row | null
): string {
  if (!assessment) {
    return "The user has not completed an assessment yet. Encourage them to take one; do not invent any score.";
  }

  const cards = lifestyleCards(assessment)
    .map(
      (card) =>
        `${card.label}: ${card.value}${
          card.unit ? ` ${card.unit}` : ""
        } (${card.tag})`
    )
    .join("; ");

  const insights = buildInsights(assessment)
    .map(
      (insight) => `${insight.title}: ${insight.text}`
    )
    .join(" | ");

  const analysis = (result?.["feature_analysis"] ?? {}) as {
    feature_importance?: {
      feature: string;
      importance: number;
    }[];
  };

  const factors = Array.isArray(analysis.feature_importance)
    ? analysis.feature_importance
        .map(
          (factor) =>
            `${prettyFeature(factor.feature)} (${factor.importance.toFixed(
              3
            )})`
        )
        .join(", ")
    : "not available";

  const modelScore = result?.["mental_health_score"];

  return [
    `Latest assessment inputs: age ${assessment.age}, gender ${assessment.gender}, country ${assessment.country}, academic level ${assessment.academic_level}, most used platform ${assessment.most_used_platform}, purpose ${assessment.purpose_of_use}, average daily usage ${assessment.avg_daily_usage_hours}h, daily unlocks ${assessment.daily_unlocks}, study ${assessment.study_hours}h, physical activity ${assessment.physical_activity_hours}h, sleep ${assessment.sleep_hours_per_night}h, self-reported stress ${assessment.stress_level}.`,
    modelScore !== null && modelScore !== undefined
      ? `Model output: mental health score ${Number(
          modelScore
        ).toFixed(1)}/10, status "${String(
          result?.["score_category"] ?? "Unknown"
        )}". Top model factors by importance: ${factors}.`
      : "No model score is available for this assessment yet — the prediction service has not returned a score. Never guess or estimate a score.",
    `Lifestyle summary: ${cards}.`,
    `Guidance already shown in the app: ${insights}`,
  ].join("\n");
}

export const sendChatMessage = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .validator((input: unknown) =>
    z
      .object({
        message: z.string().min(1).max(2000),
      })
      .parse(input)
  )
  .handler(
    async ({
      data,
      context,
    }): Promise<{ reply: ChatMessage }> => {
      const { supabase, userId } = context;

      const [
        { data: assessments },
        { data: results },
        { data: history },
      ] = await Promise.all([
        supabase
          .from("assessments")
          .select("*")
          .eq("user_id", userId)
          .order("created_at", { ascending: false })
          .limit(2),
        supabase
          .from("prediction_results")
          .select("*")
          .eq("user_id", userId)
          .order("created_at", { ascending: false })
          .limit(2),
        supabase
          .from("chat_messages")
          .select("*")
          .eq("user_id", userId)
          .order("created_at", { ascending: true })
          .limit(40),
      ]);

      const latest = (assessments?.[0] ?? null) as
        | AssessmentInput
        | null;

      const latestResult = (results?.[0] ?? null) as
        | Row
        | null;

      const previousResult = (results?.[1] ?? null) as
        | Row
        | null;

      const previousScore =
        previousResult?.["mental_health_score"];

      const comparison =
        previousScore !== null && previousScore !== undefined
          ? `Previous model score: ${Number(
              previousScore
            ).toFixed(1)}/10 on ${String(
              previousResult?.["created_at"] ?? ""
            ).slice(0, 10)}.`
          : "There is no earlier result to compare with.";

      const system = [
        "You are the VRITTACARE Wellness Assistant inside a student mental-health dashboard.",
        "Answer only from the user's saved data below. Be warm, concrete and brief (max ~120 words).",
        "Never invent, estimate or recalculate a mental health score — scores come only from the trained model.",
        "You are not a clinician; for signs of crisis, gently suggest reaching out to a professional or trusted person.",
        "",
        buildContext(latest, latestResult),
        comparison,
      ].join("\n");

      const apiKey = process.env["GEMINI_API_KEY"];

      if (!apiKey) {
        throw new Error(
          "The assistant is not configured (missing Gemini API key)."
        );
      }

      const priorMessages = (history ?? []).map((row) => {
        const message = row as Row;

        return {
          role: message["role"] as "user" | "assistant",
          content: message["message"] as string,
        };
      });

      const geminiMessages = [
        ...priorMessages.map((message) => ({
          role:
            message.role === "assistant" ? "model" : "user",
          parts: [{ text: message.content }],
        })),
        {
          role: "user",
          parts: [{ text: data.message }],
        },
      ];

      const requestBody = {
        system_instruction: {
          parts: [{ text: system }],
        },
        contents: geminiMessages,
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 500,
        },
      };

      let text = "";
      let lastError = "";

      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key=${apiKey}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(requestBody),
            }
          );

          const result = await response.json();

          if (!response.ok) {
            lastError =
              result?.error?.message ??
              `Gemini request failed with status ${response.status}`;

            const isTemporary =
              response.status === 429 ||
              response.status === 503 ||
              lastError.includes("high demand") ||
              lastError.includes("overloaded");

            if (isTemporary && attempt < 2) {
              await new Promise((resolve) =>
                setTimeout(resolve, 3000 * (attempt + 1))
              );

              continue;
            }

            throw new Error(lastError);
          }

          text =
            result?.candidates?.[0]?.content?.parts
              ?.map(
                (part: { text?: string }) => part.text ?? ""
              )
              .join("")
              .trim() ?? "";

          break;
        } catch (error) {
          lastError =
            (error as Error).message ??
            "Unknown Gemini error";

          if (attempt < 2) {
            await new Promise((resolve) =>
              setTimeout(resolve, 3000 * (attempt + 1))
            );

            continue;
          }
        }
      }

      if (!text) {
        if (
          lastError.includes("high demand") ||
          lastError.includes("overloaded") ||
          lastError.includes("429")
        ) {
          throw new Error(
            "The assistant is busy right now. Please try again in a moment."
          );
        }

        throw new Error(
          `The assistant could not respond: ${lastError}`
        );
      }

      const { data: inserted, error } = await supabase
        .from("chat_messages")
        .insert([
          {
            user_id: userId,
            role: "user",
            message: data.message,
          },
          {
            user_id: userId,
            role: "assistant",
            message: text,
          },
        ])
        .select("*");

      if (error) {
        throw new Error(
          `Could not save the conversation: ${error.message}`
        );
      }

      const assistantRow = (inserted ?? []).find(
        (row) => (row as Row)["role"] === "assistant"
      );

      return {
        reply: assistantRow
          ? toMessage(assistantRow as Row)
          : {
              id: crypto.randomUUID(),
              role: "assistant",
              content: text,
              created_at: new Date().toISOString(),
            },
      };
    }
  );