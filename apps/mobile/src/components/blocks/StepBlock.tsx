import { Text, View } from 'react-native';
import { StepBlock as StepBlockType } from '@sarathi/api-types/blocks';

export function StepBlock({ block }: { block: StepBlockType }) {
  return <View style={{ marginVertical: 8 }}><Text>{block.content}</Text></View>;
}
