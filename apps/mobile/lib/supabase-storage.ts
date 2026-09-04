import * as SecureStore from 'expo-secure-store';

const CHUNK_SIZE = 2000; // Safe limit under 2KB for Android/iOS SecureStore

export const SupabaseStorage = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      const numChunksStr = await SecureStore.getItemAsync(`${key}_chunks`);
      if (!numChunksStr) {
        // Fallback for unchunked legacy values
        return await SecureStore.getItemAsync(key);
      }
      
      const numChunks = parseInt(numChunksStr, 10);
      let fullValue = '';
      for (let i = 0; i < numChunks; i++) {
        const chunk = await SecureStore.getItemAsync(`${key}_chunk_${i}`);
        if (chunk) {
          fullValue += chunk;
        }
      }
      return fullValue;
    } catch (e) {
      console.error('Error retrieving Supabase session', e);
      return null;
    }
  },

  setItem: async (key: string, value: string): Promise<void> => {
    try {
      // First, delete any old unchunked value if we switch to chunks, or chunked if we switch to unchunked
      // To be safe, we will just clear old stuff when overwriting.
      // Since cleanup of potentially larger old chunks is complex, we'll assume standard replacement.
      if (value.length <= CHUNK_SIZE) {
        await SecureStore.deleteItemAsync(`${key}_chunks`);
        await SecureStore.setItemAsync(key, value);
        return;
      }

      // Chunk it
      const numChunks = Math.ceil(value.length / CHUNK_SIZE);
      await SecureStore.setItemAsync(`${key}_chunks`, numChunks.toString());
      for (let i = 0; i < numChunks; i++) {
        const start = i * CHUNK_SIZE;
        const chunk = value.substring(start, start + CHUNK_SIZE);
        await SecureStore.setItemAsync(`${key}_chunk_${i}`, chunk);
      }
    } catch (e) {
      console.error('Error saving Supabase session', e);
    }
  },

  removeItem: async (key: string): Promise<void> => {
    try {
      const numChunksStr = await SecureStore.getItemAsync(`${key}_chunks`);
      if (numChunksStr) {
        const numChunks = parseInt(numChunksStr, 10);
        for (let i = 0; i < numChunks; i++) {
          await SecureStore.deleteItemAsync(`${key}_chunk_${i}`);
        }
        await SecureStore.deleteItemAsync(`${key}_chunks`);
      }
      
      // Also delete the unchunked key just in case
      await SecureStore.deleteItemAsync(key);
    } catch (e) {
      console.error('Error removing Supabase session', e);
    }
  },
};
