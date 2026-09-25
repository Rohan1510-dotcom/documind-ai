
"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";

type Source = {
  document_id: number;
  chunk_index: number;
  similarity: number;
  content: string;
};

type Message = {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

type QuestionBoxProps = {
  documentId: number;
  conversationId: number;
  onAnswer: (answer: string, sources: Source[]) => void;
  onMessagesUpdate: (messages: Message[]) => void;
};

export default function QuestionBox({
  documentId,
  conversationId,
  onAnswer,
  onMessagesUpdate,
}: QuestionBoxProps) {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [message, setMessage] = useState("");

  async function handleAskQuestion() {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    const currentQuestion = question.trim();

    setAsking(true);
    setMessage("");

    try {
      const result = await askQuestion(
        documentId,
        conversationId,
        currentQuestion
      );

      onAnswer(result.answer, result.sources);

      const now = new Date().toISOString();

      const userMessage: Message = {
        id: Date.now(),
        conversation_id: conversationId,
        role: "user",
        content: currentQuestion,
        created_at: now,
      };

      const assistantMessage: Message = {
        id: Date.now() + 1,
        conversation_id: conversationId,
        role: "assistant",
        content: result.answer,
        created_at: now,
      };

      onMessagesUpdate([
        userMessage,
        assistantMessage,
      ]);

      setQuestion("");
    } catch (error) {
      console.error("Question request failed:", error);
      setMessage("Could not get an answer. Please try again.");
    } finally {
      setAsking(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleAskQuestion();
    }
  }

  return (
    <div className="mt-6 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-900/[0.03] sm:p-6">
      {/* Heading */}
      <div className="mb-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="h-5 w-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7 18.5 3.5 20l1.2-4A8.5 8.5 0 1 1 7 18.5Z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 10h8M8 14h5"
              />
            </svg>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Ask a question
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Get answers based on your document.
            </p>
          </div>
        </div>
      </div>

      {/* Question Input */}
      <div className="relative rounded-2xl border border-slate-200 bg-slate-50/70 transition-all duration-200 focus-within:border-indigo-300 focus-within:bg-white focus-within:ring-4 focus-within:ring-indigo-50">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your document..."
          disabled={asking}
          aria-label="Ask a question about your document"
          className="min-h-32 w-full resize-y rounded-2xl bg-transparent px-4 py-4 pb-16 text-sm leading-7 text-slate-800 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-60 sm:px-5"
        />

        <div className="absolute bottom-3 left-4 right-3 flex items-center justify-between gap-3 sm:left-5">
          <span className="text-xs text-slate-400">
            {asking ? "Generating answer..." : "AI-powered document search"}
          </span>

          <button
            type="button"
            onClick={handleAskQuestion}
            disabled={asking || !question.trim()}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-600/15 transition-all duration-200 hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
          >
            {asking ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Thinking
              </>
            ) : (
              <>
                Ask
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  className="h-4 w-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 12h14m-6-6 6 6-6 6"
                  />
                </svg>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Keyboard Hint */}
      <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-400">
        <span className="inline-flex items-center gap-1.5">
          <kbd className="rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-sans text-[10px] font-medium text-slate-500">
            Enter
          </kbd>
          to ask
        </span>

        <span className="text-slate-300">·</span>

        <span className="inline-flex items-center gap-1.5">
          <kbd className="rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-sans text-[10px] font-medium text-slate-500">
            Shift + Enter
          </kbd>
          for a new line
        </span>
      </div>

      {/* Error Message */}
      {message && (
        <div
          role="alert"
          className="mt-4 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className="h-5 w-5 shrink-0"
          >
            <circle cx="12" cy="12" r="9" />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 8v4m0 4h.01"
            />
          </svg>

          <p>{message}</p>
        </div>
      )}
    </div>
  );
}