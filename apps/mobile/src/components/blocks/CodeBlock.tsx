import { Text, View } from 'react-native';
import { CodeBlock as CodeBlockType } from '@sarathi/api-types/blocks';

export function CodeBlock({ block }: { block: CodeBlockType }) {
  return <View style={{ backgroundColor: "#f0f0f0", padding: 8, borderRadius: 4, marginVertical: 4 }}><Text style={{ fontFamily: "monospace" }}>{block.code}</Text></View>;
}
