const fs = require('fs');
const path = require('path');

const blocks = [
  { name: 'HeadingBlock', type: 'HeadingBlock', content: 'return <Text style={{ fontSize: 24, fontWeight: "bold", marginVertical: 8 }}>{block.text}</Text>;' },
  { name: 'TextBlock', type: 'TextBlock', content: 'return <Text style={{ fontSize: 16, marginVertical: 4 }}>{block.content}</Text>;' },
  { name: 'ListBlock', type: 'ListBlock', content: 'return <View style={{ marginVertical: 4 }}>{block.items.map((item, i) => <Text key={i} style={{ fontSize: 16 }}>• {item}</Text>)}</View>;' },
  { name: 'CodeBlock', type: 'CodeBlock', content: 'return <View style={{ backgroundColor: "#f0f0f0", padding: 8, borderRadius: 4, marginVertical: 4 }}><Text style={{ fontFamily: "monospace" }}>{block.code}</Text></View>;' },
  { name: 'MathBlock', type: 'MathBlock', content: 'return <Text style={{ fontSize: 16, marginVertical: 4, fontStyle: "italic" }}>{block.expression}</Text>;' },
  { name: 'CalloutBlock', type: 'CalloutBlock', content: 'return <View style={{ backgroundColor: "#e0f7fa", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.title || block.variant}</Text><Text>{block.content}</Text></View>;' },
  { name: 'ExampleBlock', type: 'ExampleBlock', content: 'return <View style={{ backgroundColor: "#fdf6e3", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.title || "Example"}</Text><Text>{block.content}</Text></View>;' },
  { name: 'AnalogyBlock', type: 'AnalogyBlock', content: 'return <View style={{ backgroundColor: "#f3e5f5", padding: 12, borderRadius: 8, marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>Analogy</Text><Text>{block.content}</Text></View>;' },
  { name: 'StepBlock', type: 'StepBlock', content: 'return <View style={{ marginVertical: 8 }}><Text>{block.content}</Text></View>;' },
  { name: 'QuizInlineBlock', type: 'QuizInlineBlock', content: 'return <View style={{ marginVertical: 8 }}><Text style={{ fontWeight: "bold" }}>{block.question}</Text>{block.options.map((opt, i) => <Text key={i}>○ {opt}</Text>)}</View>;' },
  { name: 'ImagePromptBlock', type: 'ImagePromptBlock', content: 'return <View style={{ height: 200, backgroundColor: "#eee", justifyContent: "center", alignItems: "center", marginVertical: 8 }}><Text>{block.alt_text}</Text></View>;' },
  { name: 'DividerBlock', type: 'DividerBlock', content: 'return <View style={{ height: 1, backgroundColor: "#ccc", marginVertical: 16 }} />;' },
];

const dir = path.join(__dirname);

blocks.forEach(b => {
  const fileContent = `import { Text, View } from 'react-native';
import { ${b.type} as ${b.type}Type } from '@sarathi/api-types/blocks';

export function ${b.name}({ block }: { block: ${b.type}Type }) {
  ${b.content}
}
`;
  fs.writeFileSync(path.join(dir, b.name + '.tsx'), fileContent);
});

const unknownBlock = `import { Text, View } from 'react-native';

export function UnknownBlock({ type }: { type: string }) {
  return <View style={{ backgroundColor: 'red', padding: 8 }}><Text style={{ color: 'white' }}>Unknown block: {type}</Text></View>;
}
`;
fs.writeFileSync(path.join(dir, 'UnknownBlock.tsx'), unknownBlock);
