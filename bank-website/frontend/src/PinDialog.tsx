import { forwardRef, useId, useState } from "react";
import { Loader2, X, AlertCircle } from "lucide-react";
import { checkCredit, NotFound, PIN_RE, type CreditResult } from "./api";

// Demo convenience: one PIN per risk band from bank-website/db/bank.db
const DEMO_PINS = [["2QPR75P", "Low"], ["0JPKL0B", "Medium"], ["2H3TZR6", "High"]] as const;

const PinDialog = forwardRef<HTMLDialogElement, { onResult: (r: CreditResult) => void; onNotFound: (pin: string) => void }>(({ onResult, onNotFound }, ref) => {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const id = useId();

  const submit = async (e: React.SyntheticEvent, value = pin) => {
    e.preventDefault();
    if (!PIN_RE.test(value)) {
      setError("Use exactly 7 characters: capital letters and numbers, with at least one of each.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      onResult(await checkCredit(value));
      setPin("");
    } catch (err) {
      if (err instanceof NotFound) { setPin(""); onNotFound(value); return; }
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <dialog ref={ref} aria-labelledby={`${id}-t`} onClose={() => setError("")}
      className="m-auto w-[min(26rem,calc(100%-2rem))] rounded-2xl border border-line bg-surface p-0 text-fg shadow-card">
      <form onSubmit={submit} className="p-6" noValidate>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id={`${id}-t`} className="text-xl font-semibold">Enter your PIN</h2>
            <p id={`${id}-h`} className="mt-1 text-sm text-fg-muted">7 characters from your ID card. Capital letters and numbers.</p>
          </div>
          <button type="button" aria-label="Close" onClick={(e) => (e.currentTarget.closest("dialog") as HTMLDialogElement).close()}
            className="grid size-11 shrink-0 cursor-pointer place-items-center rounded-lg text-fg-muted hover:bg-muted"><X size={20} aria-hidden /></button>
        </div>

        <label htmlFor={id} className="mt-5 block text-sm font-medium">PIN</label>
        <input id={id} value={pin} autoFocus autoComplete="off" autoCapitalize="characters" spellCheck={false} maxLength={7}
          aria-describedby={error ? `${id}-h ${id}-e` : `${id}-h`} aria-invalid={!!error}
          onChange={(e) => { setPin(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "")); setError(""); }}
          placeholder="e.g. 2QPR75P"
          className="mt-1 h-14 w-full rounded-xl border border-line bg-bg px-4 text-center font-mono text-2xl tracking-[0.3em] placeholder:text-base placeholder:tracking-normal placeholder:text-fg-muted aria-invalid:border-high" />
        <div className="mt-1 flex justify-between gap-3 text-xs text-fg-muted">
          <span id={`${id}-e`} role="alert" className="flex items-start gap-1 text-high">{error && <><AlertCircle size={14} className="mt-0.5 shrink-0" aria-hidden />{error}</>}</span>
          <span className="tabular-nums">{pin.length}/7</span>
        </div>

        <button type="submit" disabled={busy}
          className="mt-4 flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-brand font-semibold text-on-brand transition hover:brightness-110 disabled:cursor-wait disabled:opacity-60">
          {busy ? <><Loader2 size={18} className="animate-spin" aria-hidden /> Checking…</> : "Check my credit"}
        </button>

        <div className="mt-5 border-t border-line pt-4">
          <p className="mb-2 text-xs text-fg-muted">Demo: try a sample PIN</p>
          <div className="flex flex-wrap gap-2">
            {DEMO_PINS.map(([p, band]) => (
              <button key={p} type="button" disabled={busy} onClick={(e) => { setPin(p); submit(e, p); }}
                className="min-h-11 cursor-pointer rounded-lg border border-line px-3 font-mono text-sm hover:bg-muted">
                {p} <span className="font-sans text-xs text-fg-muted">· {band}</span>
              </button>
            ))}
          </div>
        </div>
      </form>
    </dialog>
  );
});
export default PinDialog;
