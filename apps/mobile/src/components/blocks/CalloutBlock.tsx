import { Text, View } from 'react-native';
import { CalloutBlock as CalloutBlockType } from '@sarathi/api-types/blocks';

export function CalloutBlock({ block }: { block: CalloutBlockType }) {
  return <View style={{ backgroundColor: "#e0f7fa", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.title || block.variant}</Text><Text>{block.content}</Text></View>;
}
