import { Text, View } from 'react-native';
import { MathBlock as MathBlockType } from '@sarathi/api-types/blocks';

export function MathBlock({ block }: { block: MathBlockType }) {
  return <Text style={{ fontSize: 16, marginVertical: 4, fontStyle: "italic" }}>{block.expression}</Text>;
}
