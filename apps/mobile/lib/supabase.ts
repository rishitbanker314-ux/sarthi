import { createClient } from '@supabase/supabase-js';
import { SupabaseStorage } from './supabase-storage';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || 'http://localhost:54321';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'dummy';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: SupabaseStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
