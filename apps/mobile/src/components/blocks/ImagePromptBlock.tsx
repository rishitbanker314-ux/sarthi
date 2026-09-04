import { Text, View } from 'react-native';
import { ImagePromptBlock as ImagePromptBlockType } from '@sarathi/api-types/blocks';

export function ImagePromptBlock({ block }: { block: ImagePromptBlockType }) {
  return <View style={{ height: 200, backgroundColor: "#eee", justifyContent: "center", alignItems: "center", marginVertical: 8 }}><Text>{block.alt_text}</Text></View>;
}
