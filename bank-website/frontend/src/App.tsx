import { useRef, useState } from "react";
import { BadgeCheck, Clock, Landmark, Lock, ShieldCheck, ArrowRight, Sparkles } from "lucide-react";
import PinDialog from "./PinDialog";
import Result from "./Result";
import ApplyForm from "./ApplyForm";
import type { CreditResult } from "./api";

const STEPS = [
  { icon: Lock, title: "Enter your PIN", text: "Just the 7-character PIN from your ID. No forms, no documents." },
  { icon: Clock, title: "Instant assessment", text: "We review your profile in seconds, not days." },
  { icon: BadgeCheck, title: "Clear next step", text: "See your risk level and the factors behind it, in plain language." },
];

export default function App() {
  const dialog = useRef<HTMLDialogElement>(null);
  const [result, setResult] = useState<CreditResult | null>(null);
  const [newPin, setNewPin] = useState<string | null>(null); // PIN not in DB → application form

  const open = () => dialog.current?.showModal();
  const done = (r: CreditResult) => {
    dialog.current?.close();
    setNewPin(null);
    setResult(r);
    window.scrollTo({ top: 0 });
  };

  const notFound = (pin: string) => {
    dialog.current?.close();
    setNewPin(pin);
    window.scrollTo({ top: 0 });
  };

  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-4 focus:py-2">Skip to content</a>
      <header className="sticky top-0 z-10 border-b border-line bg-surface/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <a href="/" className="flex items-center gap-2 font-semibold" aria-label="Demo Bank home">
            <span className="grid size-9 place-items-center rounded-lg bg-brand text-on-brand"><Landmark size={20} aria-hidden /></span>
            Demo Bank
          </a>
          {!result && !newPin && (
            <button onClick={open} className="min-h-11 cursor-pointer rounded-lg px-4 text-sm font-medium text-brand transition-colors hover:bg-brand-soft">
              Request credit
            </button>
          )}
        </div>
      </header>

      <main id="main" className="mx-auto max-w-6xl px-4">
        {result ? (
          <Result result={result} onBack={() => setResult(null)} />
        ) : newPin ? (
          <ApplyForm pin={newPin} onDone={done} onBack={() => setNewPin(null)} />
        ) : (
          <>
            <section className="rise grid gap-10 py-16 md:grid-cols-[1.2fr_1fr] md:items-center md:py-24">
              <div>
                <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-brand-soft px-3 py-1 text-sm font-medium text-low">
                  <Sparkles size={16} aria-hidden /> Smart credit check
                </p>
                <h1 className="text-balance text-4xl font-bold tracking-tight md:text-6xl">Know where you stand on credit in seconds.</h1>
                <p className="mt-5 max-w-prose text-lg text-fg-muted">Enter your PIN and get an instant, transparent assessment. A credit specialist always makes the final decision.</p>
                <div className="mt-8 flex flex-wrap items-center gap-4">
                  <button onClick={open} className="inline-flex min-h-12 cursor-pointer items-center gap-2 rounded-xl bg-brand px-6 text-base font-semibold text-on-brand shadow-card transition hover:brightness-110 active:scale-[0.98]">
                    Request credit <ArrowRight size={18} aria-hidden />
                  </button>
                  <span className="flex items-center gap-2 text-sm text-fg-muted"><ShieldCheck size={18} aria-hidden /> Your PIN is never stored in logs</span>
                </div>
              </div>
              <div aria-hidden className="hidden md:block">
                <div className="rounded-[var(--radius-card)] border border-line bg-surface p-6 shadow-card">
                  <p className="text-sm text-fg-muted">Preliminary assessment</p>
                  <p className="mt-1 text-3xl font-bold">Low risk</p>
                  <div className="mt-5 h-2 rounded-full bg-muted"><div className="h-2 w-1/4 rounded-full bg-brand" /></div>
                  <ul className="mt-6 space-y-3 text-sm">
                    {["Strong external credit score", "Stable income profile", "On-time payment history"].map((t) => (
                      <li key={t} className="flex items-center gap-2"><BadgeCheck size={18} className="text-brand" />{t}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            <section aria-labelledby="how" className="pb-20">
              <h2 id="how" className="mb-8 text-2xl font-semibold">How it works</h2>
              <ol className="grid gap-4 md:grid-cols-3">
                {STEPS.map(({ icon: Icon, title, text }, i) => (
                  <li key={title} className="rise rounded-[var(--radius-card)] border border-line bg-surface p-6 shadow-card" style={{ animationDelay: `${i * 60}ms` }}>
                    <span className="mb-4 grid size-11 place-items-center rounded-xl bg-brand-soft text-low"><Icon size={22} aria-hidden /></span>
                    <h3 className="font-semibold">{title}</h3>
                    <p className="mt-1 text-fg-muted">{text}</p>
                  </li>
                ))}
              </ol>
            </section>
          </>
        )}
      </main>

      <footer className="border-t border-line py-8 text-sm text-fg-muted">
        <p className="mx-auto max-w-6xl px-4">Demo project. Not a real bank. The assessment supports a credit specialist's decision; it does not approve or reject any application.</p>
      </footer>

      <PinDialog ref={dialog} onResult={done} onNotFound={notFound} />
    </>
  );
}
