import { useId, useState } from "react";
import { AlertCircle, ArrowLeft, Loader2, UserPlus } from "lucide-react";
import { applyCredit, type Application, type CreditResult } from "./api";

const CONTRACT = ["Cash loans", "Revolving loans"];
const INCOME = ["Working", "Commercial associate", "State servant", "Businessman", "Pensioner", "Student", "Unemployed", "Maternity leave"];
const EDUCATION = ["Secondary / secondary special", "Higher education", "Incomplete higher", "Lower secondary", "Academic degree"];
const FAMILY = ["Single / not married", "Married", "Civil marriage", "Separated", "Widow"];
const HOUSING = ["House / apartment", "With parents", "Rented apartment", "Municipal apartment", "Co-op apartment", "Office apartment"];

const input = "mt-1 h-12 w-full rounded-xl border border-line bg-bg px-3 text-base";

function Field({ label, hint, children }: { label: string; hint?: string; children: (id: string) => React.ReactNode }) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium">{label}</label>
      {children(id)}
      {hint && <p className="mt-1 text-xs text-fg-muted">{hint}</p>}
    </div>
  );
}

const Select = ({ id, name, options, def }: { id: string; name: string; options: string[]; def?: string }) => (
  <select id={id} name={name} defaultValue={def ?? options[0]} className={input}>
    {options.map((o) => <option key={o}>{o}</option>)}
  </select>
);

export default function ApplyForm({ pin, onDone, onBack }: { pin: string; onDone: (r: CreditResult) => void; onBack: () => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const today = new Date().toISOString().slice(0, 10);

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const s = (k: string) => String(f.get(k) ?? "").trim();
    const n = (k: string) => Number(f.get(k));
    const data: Application = {
      pin, first_name: s("first_name"), last_name: s("last_name"), birth_date: s("birth_date"),
      name_contract_type: s("name_contract_type"), amt_credit: n("amt_credit"), term_months: n("term_months"),
      amt_income_total: n("amt_income_total"), name_income_type: s("name_income_type"), employed_years: n("employed_years"),
      name_education_type: s("name_education_type"), name_family_status: s("name_family_status"),
      name_housing_type: s("name_housing_type"), cnt_children: n("cnt_children"),
      flag_own_car: f.get("flag_own_car") ? "Y" : "N", flag_own_realty: f.get("flag_own_realty") ? "Y" : "N",
      region_rating_client: n("region_rating_client"),
      has_work_phone: !!f.get("has_work_phone"), has_mobile_phone: !!f.get("has_mobile_phone"), has_email: !!f.get("has_email"),
    };
    setBusy(true);
    setError("");
    try {
      onDone(await applyCredit(data));
    } catch (err) {
      setError((err as Error).message);
      document.getElementById("apply-error")?.focus();
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="rise mx-auto max-w-3xl py-10 md:py-16" aria-labelledby="apply-h">
      <button onClick={onBack} className="mb-6 inline-flex min-h-11 cursor-pointer items-center gap-2 text-sm font-medium text-fg-muted hover:text-fg">
        <ArrowLeft size={16} aria-hidden /> Back
      </button>
      <p className="inline-flex items-center gap-2 rounded-full bg-brand-soft px-3 py-1 text-sm font-medium text-low"><UserPlus size={16} aria-hidden /> New customer</p>
      <h1 id="apply-h" className="mt-3 text-3xl font-bold md:text-4xl">We don't know this PIN yet</h1>
      <p className="mt-2 max-w-prose text-fg-muted">
        Tell us a little about yourself. We'll save your details with PIN <strong className="font-mono text-fg">{pin}</strong> so next time it's one step, then run your assessment.
      </p>

      <form onSubmit={submit} className="mt-8 space-y-8">
        {error && (
          <p id="apply-error" tabIndex={-1} role="alert" className="flex items-start gap-2 rounded-xl bg-high-soft p-4 text-high">
            <AlertCircle size={18} className="mt-0.5 shrink-0" aria-hidden />{error}
          </p>
        )}

        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="mb-3 text-lg font-semibold">About you</legend>
          <Field label="First name">{(id) => <input id={id} name="first_name" required maxLength={40} autoComplete="given-name" className={input} />}</Field>
          <Field label="Last name">{(id) => <input id={id} name="last_name" required maxLength={40} autoComplete="family-name" className={input} />}</Field>
          <Field label="Date of birth" hint="You must be 18 or older.">{(id) => <input id={id} name="birth_date" type="date" required max={today} autoComplete="bday" className={input} />}</Field>
          <Field label="Family status">{(id) => <Select id={id} name="name_family_status" options={FAMILY} />}</Field>
          <Field label="Children">{(id) => <input id={id} name="cnt_children" type="number" inputMode="numeric" min={0} max={15} defaultValue={0} required className={input} />}</Field>
          <Field label="Education">{(id) => <Select id={id} name="name_education_type" options={EDUCATION} />}</Field>
          <Field label="Housing">{(id) => <Select id={id} name="name_housing_type" options={HOUSING} />}</Field>
          <div className="flex flex-col justify-end gap-2 pb-1">
            <label className="flex min-h-11 items-center gap-3"><input type="checkbox" name="flag_own_realty" className="size-5 accent-[var(--brand)]" /> I own real estate</label>
            <label className="flex min-h-11 items-center gap-3"><input type="checkbox" name="flag_own_car" className="size-5 accent-[var(--brand)]" /> I own a car</label>
          </div>
        </fieldset>

        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="mb-3 text-lg font-semibold">Where you live and how we reach you</legend>
          <Field label="Region rating" hint="Our rating of your area: 1 is the highest, 3 the lowest.">
            {(id) => <select id={id} name="region_rating_client" defaultValue="2" className={input}><option value="1">1 – Highest</option><option value="2">2 – Medium</option><option value="3">3 – Lowest</option></select>}
          </Field>
          <div className="flex flex-col justify-end gap-2 pb-1">
            <label className="flex min-h-11 items-center gap-3"><input type="checkbox" name="has_mobile_phone" defaultChecked className="size-5 accent-[var(--brand)]" /> I have a mobile phone</label>
            <label className="flex min-h-11 items-center gap-3"><input type="checkbox" name="has_work_phone" className="size-5 accent-[var(--brand)]" /> I have a work phone</label>
            <label className="flex min-h-11 items-center gap-3"><input type="checkbox" name="has_email" className="size-5 accent-[var(--brand)]" /> I have an email address</label>
          </div>
        </fieldset>

        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="mb-3 text-lg font-semibold">Work and income</legend>
          <Field label="Income source">{(id) => <Select id={id} name="name_income_type" options={INCOME} />}</Field>
          <Field label="Years in current job" hint="0 if not employed.">{(id) => <input id={id} name="employed_years" type="number" inputMode="decimal" step="0.5" min={0} max={60} defaultValue={0} required className={input} />}</Field>
          <Field label="Annual income">{(id) => <input id={id} name="amt_income_total" type="number" inputMode="numeric" min={1} max={100000000} required className={input} />}</Field>
        </fieldset>

        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="mb-3 text-lg font-semibold">The credit you want</legend>
          <Field label="Credit type">{(id) => <Select id={id} name="name_contract_type" options={CONTRACT} />}</Field>
          <Field label="Amount">{(id) => <input id={id} name="amt_credit" type="number" inputMode="numeric" min={1} max={100000000} required className={input} />}</Field>
          <Field label="Term (months)" hint="6 to 360.">{(id) => <input id={id} name="term_months" type="number" inputMode="numeric" min={6} max={360} defaultValue={36} required className={input} />}</Field>
        </fieldset>

        <button type="submit" disabled={busy}
          className="flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-brand px-6 font-semibold text-on-brand shadow-card transition hover:brightness-110 disabled:cursor-wait disabled:opacity-60 sm:w-auto">
          {busy ? <><Loader2 size={18} className="animate-spin" aria-hidden /> Saving and checking…</> : "Save details and request credit"}
        </button>
        <p className="text-xs text-fg-muted">Demo only. Details are stored in the demo database. New customers have no credit-bureau history, so the assessment is less precise.</p>
      </form>
    </section>
  );
}
