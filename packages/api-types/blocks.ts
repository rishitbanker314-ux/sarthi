export type HeadingBlock = {
  id: string;
  type: "heading";
  text: string;
  level: 1 | 2 | 3 | 4 | 5 | 6;
};

export type TextBlock = {
  id: string;
  type: "text";
  content: string;
};

export type ListBlock = {
  id: string;
  type: "list";
  items: string[];
  ordered?: boolean;
};

export type CodeBlock = {
  id: string;
  type: "code";
  code: string;
  language: string;
};

export type MathBlock = {
  id: string;
  type: "math";
  expression: string;
  display?: boolean;
};

export type CalloutVariant = "info" | "tip" | "warning" | "misconception" | "ai_notice";

export type CalloutBlock = {
  id: string;
  type: "callout";
  variant: CalloutVariant;
  title?: string;
  content: string;
};

export type ExampleBlock = {
  id: string;
  type: "example";
  title?: string;
  content: string;
};

export type AnalogyBlock = {
  id: string;
  type: "analogy";
  content: string;
};

export type StepBlock = {
  id: string;
  type: "step";
  content: string;
  reveal?: boolean;
};

export type QuizInlineBlock = {
  id: string;
  type: "quiz_inline";
  question: string;
  options: string[];
  correct_option_index: number;
  feedback: string;
};

export type ImagePromptBlock = {
  id: string;
  type: "image_prompt";
  prompt: string;
  alt_text: string;
};

export type DividerBlock = {
  id: string;
  type: "divider";
};

export type ContentBlock =
  | HeadingBlock
  | TextBlock
  | ListBlock
  | CodeBlock
  | MathBlock
  | CalloutBlock
  | ExampleBlock
  | AnalogyBlock
  | StepBlock
  | QuizInlineBlock
  | ImagePromptBlock
  | DividerBlock;
