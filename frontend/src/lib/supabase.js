import { createClient } from "@supabase/supabase-js";

const url = process.env.REACT_APP_SUPABASE_URL;
const key = process.env.REACT_APP_SUPABASE_PUBLISHABLE_KEY;

export const authEnabled = Boolean(url && key && !url.includes("YOUR_") && !key.includes("REPLACE"));

export const supabase = authEnabled
  ? createClient(url, key, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } })
  : null;

// Dev-only: when Supabase is not configured, a token in localStorage (nv_dev_token) is sent as Bearer.
export const getDevToken = () => (authEnabled ? null : localStorage.getItem("nv_dev_token"));

export async function getAccessToken() {
  if (!supabase) return getDevToken();
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token || null;
}
