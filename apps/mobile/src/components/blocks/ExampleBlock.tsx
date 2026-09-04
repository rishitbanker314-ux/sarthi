import { Text, View } from 'react-native';
import { ExampleBlock as ExampleBlockType } from '@sarathi/api-types/blocks';

export function ExampleBlock({ block }: { block: ExampleBlockType }) {
  return <View style={{ backgroundColor: "#fdf6e3", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.title || "Example"}</Text><Text>{block.content}</Text></View>;
}
