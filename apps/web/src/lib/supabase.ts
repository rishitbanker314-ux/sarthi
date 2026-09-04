import { createClient } from "@supabase/supabase-js";
import { setTokenProvider } from "@sarathi/api-client";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "http://localhost:54321";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "dummy-anon-key";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Set up the API client token provider to pull from the current session
setTokenProvider(async () => {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
});
