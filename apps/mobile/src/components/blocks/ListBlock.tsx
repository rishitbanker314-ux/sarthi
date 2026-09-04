import { Text, View } from 'react-native';
import { ListBlock as ListBlockType } from '@sarathi/api-types/blocks';

export function ListBlock({ block }: { block: ListBlockType }) {
  return <View style={{ marginVertical: 4 }}>{block.items.map((item, i) => <Text key={i} style={{ fontSize: 16 }}>• {item}</Text>)}</View>;
}
