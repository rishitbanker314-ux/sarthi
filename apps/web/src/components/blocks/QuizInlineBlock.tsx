"use client";

import { QuizInlineBlock as QuizInlineBlockType } from "@sarathi/api-types";
import { useState } from "react";
import { Button } from "@sarathi/ui";
import { CheckCircle2, XCircle } from "lucide-react";

export function QuizInlineBlock({ block }: { block: QuizInlineBlockType }) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const handleSubmit = () => {
    if (selectedOption === null) return;
    setHasSubmitted(true);
    
    if (selectedOption !== block.correct_option_index) {
      // Emits inline_check_failed on wrong answer
      console.log(`inline_check_failed emitted for block ${block.id}`);
    }
  };

  const isCorrect = selectedOption === block.correct_option_index;

  return (
    <div className="my-6 p-5 rounded-xl border border-border bg-card shadow-sm">
      <h4 className="font-semibold text-lg mb-4 text-foreground">{block.question}</h4>
      
      <div className="space-y-3 mb-6">
        {block.options.map((option, idx) => {
          const isSelected = selectedOption === idx;
          const showAsCorrect = hasSubmitted && idx === block.correct_option_index;
          const showAsWrong = hasSubmitted && isSelected && !isCorrect;
          
          let optionClasses = "border-border hover:bg-muted/50 hover:border-primary/50";
          if (isSelected && !hasSubmitted) {
            optionClasses = "border-primary bg-primary/5 text-primary";
          } else if (showAsCorrect) {
            optionClasses = "border-green-500 bg-green-50 text-green-900 dark:bg-green-950/30 dark:text-green-200 dark:border-green-800";
          } else if (showAsWrong) {
            optionClasses = "border-rose-500 bg-rose-50 text-rose-900 dark:bg-rose-950/30 dark:text-rose-200 dark:border-rose-800";
          } else if (hasSubmitted) {
            optionClasses = "opacity-50 border-border bg-muted/20 cursor-not-allowed";
          }

          return (
            <div 
              key={idx}
              onClick={() => !hasSubmitted && setSelectedOption(idx)}
              className={`p-3 rounded-lg border transition-colors cursor-pointer flex items-center justify-between ${optionClasses}`}
            >
              <span>{option}</span>
              {showAsCorrect && <CheckCircle2 className="w-5 h-5 text-green-500" />}
              {showAsWrong && <XCircle className="w-5 h-5 text-rose-500" />}
            </div>
          );
        })}
      </div>

      {!hasSubmitted ? (
        <Button 
          onClick={handleSubmit} 
          disabled={selectedOption === null}
          className="w-full sm:w-auto"
        >
          Check Answer
        </Button>
      ) : (
        <div className={`p-4 rounded-lg mt-4 ${isCorrect ? 'bg-green-50/50 text-green-900 dark:bg-green-900/20 dark:text-green-100' : 'bg-rose-50/50 text-rose-900 dark:bg-rose-900/20 dark:text-rose-100'}`}>
          <p className="font-medium mb-1">
            {isCorrect ? 'Correct!' : 'Not quite.'}
          </p>
          <p className="text-sm opacity-90">{block.feedback}</p>
        </div>
      )}
    </div>
  );
}
