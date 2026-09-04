import { Text, View } from 'react-native';
import { DividerBlock as DividerBlockType } from '@sarathi/api-types/blocks';

export function DividerBlock({ block }: { block: DividerBlockType }) {
  return <View style={{ height: 1, backgroundColor: "#ccc", marginVertical: 16 }} />;
}
