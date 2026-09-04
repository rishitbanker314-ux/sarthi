import { Text, View } from 'react-native';
import { AnalogyBlock as AnalogyBlockType } from '@sarathi/api-types/blocks';

export function AnalogyBlock({ block }: { block: AnalogyBlockType }) {
  return <View style={{ backgroundColor: "#f3e5f5", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>Analogy</Text><Text>{block.content}</Text></View>;
}
