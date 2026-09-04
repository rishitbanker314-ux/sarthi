import { Text, View } from 'react-native';

export function UnknownBlock({ type }: { type: string }) {
  return <View style={{ backgroundColor: 'red', padding: 8 }}><Text style={{ color: 'white' }}>Unknown block: {type}</Text></View>;
}
