import { Activity, BookOpen, MonitorSmartphone, Moon, Wind } from "lucide-react";

import { StatusPill } from "@/components/mb/primitives";
import { lifestyleCards, type AssessmentInput } from "@/lib/mb";

const ICONS = {
  sleep: Moon,
  study: BookOpen,
  screen: MonitorSmartphone,
  activity: Activity,
  stress: Wind,
} as const;

const CONTEXT: Record<string, string> = {
  sleep: "Hours of sleep per night",
  study: "Focused study time today",
  screen: "Average daily social-media use",
  activity: "Physical movement today",
  stress: "How stressed you feel right now",
};

export function WellnessMetrics({
  assessment,
}: {
  assessment: AssessmentInput;
}) {
  const cards = lifestyleCards(assessment);

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
      {cards.map((card) => {
        const Icon = ICONS[card.key];

        return (
          <article
            key={card.key}
            className="flex min-h-[168px] flex-col justify-between rounded-2xl border border-mb-line bg-mb-panel-2/55 p-4 transition hover:border-mb-cyan/30"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="grid h-9 w-9 place-items-center rounded-xl border border-mb-line bg-background/25 text-mb-cyan">
                    <Icon className="h-[18px] w-[18px] stroke-[1.8]" />
                  </span>
                  <p className="text-sm font-bold leading-tight text-foreground">
                    {card.label}
                  </p>
                </div>
              </div>

              <p className="mt-1 text-[11px] leading-snug text-muted-foreground">
                {CONTEXT[card.key] ?? "Latest check-in signal"}
              </p>
            </div>

            <div className="mt-4">
              <p className="text-2xl font-extrabold leading-none text-foreground">
                {card.value}
                {card.unit ? (
                  <span className="ml-1 text-xs font-medium text-muted-foreground">
                    {card.unit}
                  </span>
                ) : null}
              </p>

              <div className="mt-3">
                <StatusPill tone={card.tone}>{card.tag}</StatusPill>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}