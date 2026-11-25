import { ArrowDown, ArrowLeft, ArrowUp, CircleCheck, TriangleAlert, OctagonAlert, Info } from "lucide-react";
import type { CreditResult } from "./api";

const BAND = {
  Low: { icon: CircleCheck, cls: "bg-low-soft text-low", bar: "bg-low", w: "w-1/4", text: "Your profile shows a low level of credit risk." },
  Medium: { icon: TriangleAlert, cls: "bg-mid-soft text-mid", bar: "bg-mid", w: "w-1/2", text: "Your profile shows a moderate level of credit risk." },
  High: { icon: OctagonAlert, cls: "bg-high-soft text-high", bar: "bg-high", w: "w-5/6", text: "Your profile shows an elevated level of credit risk." },
} as const;

const money = (n: number) => new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(n);

export default function Result({ result: r, onBack }: { result: CreditResult; onBack: () => void }) {
  const b = BAND[r.risk_band];
  const f = r.explanation
    ? [...r.explanation.top_positive_factors.map((x) => ({ ...x, up: true })), ...r.explanation.top_negative_factors.map((x) => ({ ...x, up: false }))]
    : [];
  const max = Math.max(...f.map((x) => Math.abs(x.contribution)), 0.01);
  const stats: [string, number | null][] = [
    ["Requested amount", r.customer.amt_credit],
    ["Annual income", r.customer.amt_income_total],
    ["Annuity", r.customer.amt_annuity],
  ];

  return (
    <section className="rise mx-auto max-w-3xl py-10 md:py-16" aria-labelledby="res">
      <button onClick={onBack} className="mb-6 inline-flex min-h-11 cursor-pointer items-center gap-2 text-sm font-medium text-fg-muted hover:text-fg">
        <ArrowLeft size={16} aria-hidden /> Back to home
      </button>
      <p className="text-fg-muted">Hello, {r.customer.first_name}</p>
      <h1 id="res" className="text-3xl font-bold md:text-4xl">Your credit assessment</h1>

      <div className="mt-6 rounded-[var(--radius-card)] border border-line bg-surface p-6 shadow-card" role="status">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <span className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-lg font-semibold ${b.cls}`}>
            <b.icon size={22} aria-hidden />{r.risk_band} risk
          </span>
          <p className="text-sm text-fg-muted">Estimated default probability <strong className="tabular-nums text-fg">{(r.prediction_probability * 100).toFixed(1)}%</strong></p>
        </div>
        <div className="mt-5 h-2 rounded-full bg-muted" aria-hidden><div className={`h-2 rounded-full ${b.bar} ${b.w}`} /></div>
        <div className="mt-1 flex justify-between text-xs text-fg-muted" aria-hidden><span>Low</span><span>Medium</span><span>High</span></div>
        <p className="mt-4">{b.text} A credit specialist will review your request and contact you with the next steps.</p>
      </div>

      <dl className="mt-4 grid gap-4 sm:grid-cols-3">
        {stats.map(([k, v]) => (
          <div key={k} className="rounded-[var(--radius-card)] border border-line bg-surface p-4">
            <dt className="text-sm text-fg-muted">{k}</dt>
            <dd className="mt-1 text-xl font-semibold tabular-nums">{v == null ? "—" : money(v)}</dd>
          </div>
        ))}
      </dl>

      {r.data_coverage < 0.5 && (
        <p className="mt-4 flex gap-2 rounded-xl bg-muted p-4 text-sm" role="note">
          <Info size={18} className="mt-0.5 shrink-0" aria-hidden />
          This is a preliminary estimate. We have limited data on you so far (for example, no credit-bureau history), and factors we have no data for are not shown below.
        </p>
      )}

      {f.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold">What shaped this result</h2>
          <p className="mt-1 text-sm text-fg-muted">The factors that moved your assessment the most. They describe the model's behavior, not a cause.</p>
          <ul className="mt-4 space-y-3">
            {f.map((x) => (
              <li key={x.feature_name} className="rounded-xl border border-line bg-surface p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium">{x.display_name}</span>
                  <span className={`inline-flex shrink-0 items-center gap-1 text-sm font-medium ${x.up ? "text-high" : "text-low"}`}>
                    {x.up ? <ArrowUp size={16} aria-hidden /> : <ArrowDown size={16} aria-hidden />}{x.up ? "Raises risk" : "Lowers risk"}
                  </span>
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-muted" aria-hidden>
                  <div className={`h-1.5 rounded-full ${x.up ? "bg-high" : "bg-low"}`} style={{ width: `${Math.max(6, (Math.abs(x.contribution) / max) * 100)}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="mt-8 flex gap-2 text-sm text-fg-muted"><Info size={18} className="shrink-0" aria-hidden />{r.disclaimer}</p>
    </section>
  );
}
