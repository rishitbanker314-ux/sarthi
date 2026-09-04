import { Text, View } from 'react-native';
import { QuizInlineBlock as QuizInlineBlockType } from '@sarathi/api-types/blocks';

export function QuizInlineBlock({ block }: { block: QuizInlineBlockType }) {
  return <View style={{ marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.question}</Text>{block.options.map((opt, i) => <Text key={i}>○ {opt}</Text>)}</View>;
}
