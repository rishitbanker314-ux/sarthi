import { Slot } from 'expo-router';
import { Providers } from '@/lib/providers';

export default function RootLayout() {
  return (
    <Providers>
      <Slot />
    </Providers>
  );
}
