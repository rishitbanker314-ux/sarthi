import { ContentBlock } from "@sarathi/api-types";
import { UnknownBlock } from "./UnknownBlock";
import { HeadingBlock } from "./HeadingBlock";
import { TextBlock } from "./TextBlock";
import { ListBlock } from "./ListBlock";
import { CodeBlock } from "./CodeBlock";
import { MathBlock } from "./MathBlock";
import { CalloutBlock } from "./CalloutBlock";
import { ExampleBlock } from "./ExampleBlock";
import { AnalogyBlock } from "./AnalogyBlock";
import { StepBlock } from "./StepBlock";
import { QuizInlineBlock } from "./QuizInlineBlock";
import { ImagePromptBlock } from "./ImagePromptBlock";
import { DividerBlock } from "./DividerBlock";

export function BlockRenderer({ block }: { block: ContentBlock | any }) {
  if (!block || typeof block !== 'object' || !block.type) {
    return <UnknownBlock block={{ type: "missing_type", ...block }} />;
  }

  switch (block.type) {
    case "heading":
      return <HeadingBlock block={block} />;
    case "text":
      return <TextBlock block={block} />;
    case "list":
      return <ListBlock block={block} />;
    case "code":
      return <CodeBlock block={block} />;
    case "math":
      return <MathBlock block={block} />;
    case "callout":
      return <CalloutBlock block={block} />;
    case "example":
      return <ExampleBlock block={block} />;
    case "analogy":
      return <AnalogyBlock block={block} />;
    case "step":
      return <StepBlock block={block} />;
    case "quiz_inline":
      return <QuizInlineBlock block={block} />;
    case "image_prompt":
      return <ImagePromptBlock block={block} />;
    case "divider":
      return <DividerBlock block={block} />;
    default:
      return <UnknownBlock block={block} />;
  }
}
