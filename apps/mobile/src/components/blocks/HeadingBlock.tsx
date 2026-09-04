import { Text, View } from 'react-native';
import { HeadingBlock as HeadingBlockType } from '@sarathi/api-types/blocks';

export function HeadingBlock({ block }: { block: HeadingBlockType }) {
  return <Text style={{ fontSize: 24, fontWeight: "bold", marginVertical: 8 }}>{block.text}</Text>;
}
