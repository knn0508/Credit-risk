export type Factor = { feature_name: string; display_name: string; contribution: number };
export type CreditResult = {
  customer: { first_name: string; last_name: string; amt_income_total: number; amt_credit: number; amt_annuity: number | null; name_contract_type: string };
  prediction_id: string;
  data_coverage: number;
  prediction_probability: number;
  risk_band: "Low" | "Medium" | "High";
  explanation: { top_positive_factors: Factor[]; top_negative_factors: Factor[] } | null;
  disclaimer: string;
};

export const PIN_RE = /^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{7}$/;

export class NotFound extends Error {}

const BASE = import.meta.env.VITE_API_URL ?? ""; // prod: Worker URL; dev: "" (Vite proxy)

async function post(path: string, body: unknown): Promise<Response> {
  try {
    return await fetch(BASE + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  } catch {
    throw new Error("Can't reach the service. Check your connection and try again.");
  }
}

export async function checkCredit(pin: string): Promise<CreditResult> {
  const r = await post("/bank/credit-check", { pin });
  if (r.status === 404) throw new NotFound();
  if (!r.ok) throw new Error("Something went wrong on our side. Please try again in a moment.");
  return r.json();
}

export type Application = {
  pin: string; first_name: string; last_name: string; birth_date: string;
  name_contract_type: string; amt_credit: number; term_months: number; amt_income_total: number;
  name_income_type: string; employed_years: number; name_education_type: string; name_family_status: string;
  name_housing_type: string; cnt_children: number; flag_own_car: string; flag_own_realty: string;
  region_rating_client: number; has_work_phone: boolean; has_mobile_phone: boolean; has_email: boolean;
};

// Backend saves the applicant to the DB first, then scores.
export async function applyCredit(a: Application): Promise<CreditResult> {
  const r = await post("/bank/apply", a);
  if (r.status === 409) throw new Error("This PIN is already registered. Go back and enter it again to see your result.");
  if (r.status === 422) throw new Error("Some details look invalid. Please check the form (age must be 18–80).");
  if (!r.ok) throw new Error("We couldn't process your request. Your details may be saved; please try again later.");
  return r.json();
}
