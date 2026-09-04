import { createClient } from "@supabase/supabase-js";
import * as SecureStore from "expo-secure-store";

const CHUNK_SIZE = 2000; // Just under 2KB

const chunkingAdapter = {
  getItem: async (key: string) => {
    try {
      const chunkCountStr = await SecureStore.getItemAsync(key + "_count");
      if (!chunkCountStr) return null;
      const count = parseInt(chunkCountStr, 10);
      let fullString = "";
      for (let i = 0; i < count; i++) {
        const chunk = await SecureStore.getItemAsync(key + "_" + i);
        if (chunk) fullString += chunk;
      }
      return fullString || null;
    } catch (e) {
      console.error("SecureStore getItem error:", e);
      return null;
    }
  },
  setItem: async (key: string, value: string) => {
    try {
      const chunks = Math.ceil(value.length / CHUNK_SIZE);
      await SecureStore.setItemAsync(key + "_count", chunks.toString());
      for (let i = 0; i < chunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = start + CHUNK_SIZE;
        await SecureStore.setItemAsync(key + "_" + i, value.substring(start, end));
      }
    } catch (e) {
      console.error("SecureStore setItem error:", e);
    }
  },
  removeItem: async (key: string) => {
    try {
      const chunkCountStr = await SecureStore.getItemAsync(key + "_count");
      if (chunkCountStr) {
        const count = parseInt(chunkCountStr, 10);
        for (let i = 0; i < count; i++) {
          await SecureStore.deleteItemAsync(key + "_" + i);
        }
        await SecureStore.deleteItemAsync(key + "_count");
      }
    } catch (e) {
      console.error("SecureStore removeItem error:", e);
    }
  },
};

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || "";

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: chunkingAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
