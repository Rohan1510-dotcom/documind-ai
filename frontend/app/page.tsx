
"use client";

import { useEffect, useState } from "react";
import UploadBox from "./components/UploadBox";
import QuestionBox from "./components/QuestionBox";
import SourcesCard from "./components/SourcesCard";
import DocumentCard from "./components/DocumentCard";
import ChatMessage from "./components/ChatMessage";
import {
  createConversation,
  getConversationMessages,
  deleteDocument,
} from "../lib/api";

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

export default function Home() {
  const [documentId, setDocumentId] = useState<number | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [filename, setFilename] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);

  async function handleUploadSuccess(
    uploadedDocumentId: number,
    uploadedFilename: string
  ) {
    try {
      const conversation = await createConversation(uploadedDocumentId);

      setDocumentId(uploadedDocumentId);
      setConversationId(conversation.id);
      setFilename(uploadedFilename);
      setMessages([]);
      setSources([]);

      const conversationMessages = await getConversationMessages(
        conversation.id
      );

      setMessages(conversationMessages);
    } catch (error) {
      console.error("Failed to create conversation:", error);
      alert("Document uploaded, but conversation could not be created.");
    }
  }

  async function handleDeleteDocument(id: number) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this document? This action cannot be undone."
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteDocument(id);

      setDocumentId(null);
      setConversationId(null);
      setFilename("");
      setMessages([]);
      setSources([]);
    } catch (error) {
      console.error("Failed to delete document:", error);
      alert("Failed to delete document. Please try again.");
    }
  }

  useEffect(() => {
    async function loadMessages() {
      if (!conversationId) {
        return;
      }

      try {
        const conversationMessages = await getConversationMessages(
          conversationId
        );

        setMessages(conversationMessages);
      } catch (error) {
        console.error("Failed to load conversation messages:", error);
      }
    }

    loadMessages();
  }, [conversationId]);

  function handleAnswer(
    newAnswer: string,
    newSources: Source[]
  ) {
    setSources(newSources);
  }

  function handleMessagesUpdate(newMessages: Message[]) {
    setMessages((previousMessages) => [
      ...previousMessages,
      ...newMessages,
    ]);
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#f5f7fb] text-slate-900">
      {/* Background accents */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-indigo-200/30 blur-3xl" />
        <div className="absolute -left-40 top-[500px] h-[400px] w-[400px] rounded-full bg-blue-200/20 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-6xl px-5 py-8 sm:px-8 lg:px-10">
        {/* Header */}
        <header className="mb-10 flex flex-col gap-5 border-b border-slate-200/80 pb-7 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-xl font-bold text-white shadow-lg shadow-slate-900/15">
              D
            </div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">
                DocuMind <span className="text-indigo-600">AI</span>
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Intelligent Document Intelligence Platform
              </p>
            </div>
          </div>

          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-4 py-2 text-sm font-medium text-slate-600 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            AI workspace
          </div>
        </header>

        {/* Hero */}
        <section className="mb-9">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-indigo-700">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
            Your intelligent document assistant
          </div>

          <h2 className="max-w-3xl text-3xl font-bold leading-tight tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">
            Your documents.
            <br className="hidden sm:block" />{" "}
            <span className="text-indigo-600">
              Answers in seconds.
            </span>
          </h2>

          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-500 sm:text-lg">
            Upload a document, ask questions in natural language, and explore
            relevant information with AI-powered search.
          </p>
        </section>

        {/* Main workspace */}
        <section className="space-y-6">
          {/* Upload */}
          <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-900/[0.03] sm:p-8">
            <div className="mb-6 flex items-start gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
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
                    d="M12 16V4m0 0L7 9m5-5 5 5M5 15v4a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-4"
                  />
                </svg>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Upload your document
                </h3>
                <p className="mt-1 text-sm leading-6 text-slate-500">
                  Add a PDF to start exploring its contents with AI.
                </p>
              </div>
            </div>

            <UploadBox onUploadSuccess={handleUploadSuccess} />
          </div>

          {/* Document */}
          {documentId && (
            <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-900/[0.03] sm:p-7">
              <div className="mb-5 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
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
                      d="M7 3.75h7l5 5v11.5H7a2 2 0 0 1-2-2v-12.5a2 2 0 0 1 2-2Z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M14 3.75v5h5M9 13h6M9 16.5h6"
                    />
                  </svg>
                </div>

                <div>
                  <h3 className="font-semibold text-slate-900">
                    Current document
                  </h3>
                  <p className="text-sm text-slate-500">
                    Your uploaded file
                  </p>
                </div>
              </div>

              <DocumentCard
                filename={filename}
                documentId={documentId}
                onDelete={handleDeleteDocument}
              />
            </div>
          )}

          {/* Chat */}
          {documentId && conversationId && (
            <div className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-sm shadow-slate-900/[0.03]">
              <div className="flex items-center gap-4 border-b border-slate-100 px-5 py-5 sm:px-7">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20">
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
                  <h3 className="text-lg font-semibold text-slate-900">
                    Chat with your document
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Ask questions and get answers grounded in your PDF.
                  </p>
                </div>
              </div>

              <div className="space-y-5 bg-slate-50/60 px-4 py-6 sm:px-7 sm:py-8">
                {messages.length > 0 ? (
                  messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      role={message.role}
                      content={message.content}
                    />
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-slate-200 bg-white px-5 py-10 text-center">
                    <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        className="h-6 w-6"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M12 3v2m0 14v2M3 12h2m14 0h2M5.64 5.64l1.42 1.42m9.88 9.88 1.42 1.42m0-12.72-1.42 1.42m-9.88 9.88-1.42 1.42"
                        />
                        <circle cx="12" cy="12" r="5" />
                      </svg>
                    </div>
                    <p className="font-medium text-slate-800">
                      Ready when you are
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                      Ask your first question below to get started.
                    </p>
                  </div>
                )}

                <QuestionBox
                  documentId={documentId}
                  conversationId={conversationId}
                  onAnswer={handleAnswer}
                  onMessagesUpdate={handleMessagesUpdate}
                />
              </div>
            </div>
          )}

          {/* Sources */}
          <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-900/[0.03] sm:p-7">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
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
                    d="M8 4h8a2 2 0 0 1 2 2v14H6V6a2 2 0 0 1 2-2Z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 9h6M9 12.5h6M9 16h4"
                  />
                </svg>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900">
                  Reference sources
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Relevant document passages used to support your answers.
                </p>
              </div>
            </div>

            <SourcesCard sources={sources} />
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-12 border-t border-slate-200/80 py-6 text-center">
          <p className="text-xs text-slate-400">
            DocuMind AI · Intelligent Document Intelligence
          </p>
        </footer>
      </div>
    </main>
  );
}