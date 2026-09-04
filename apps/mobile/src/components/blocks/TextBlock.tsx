import { Text, View } from 'react-native';
import { TextBlock as TextBlockType } from '@sarathi/api-types/blocks';

export function TextBlock({ block }: { block: TextBlockType }) {
  return <Text style={{ fontSize: 16, marginVertical: 4 }}>{block.content}</Text>;
}
