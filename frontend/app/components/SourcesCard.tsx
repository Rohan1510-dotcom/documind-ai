
"use client";

import { useState } from "react";

type Source = {
  document_id: number;
  chunk_index: number;
  similarity: number;
  content: string;
};

type SourcesCardProps = {
  sources: Source[];
};

export default function SourcesCard({
  sources,
}: SourcesCardProps) {
  const [expandedSource, setExpandedSource] = useState<
    number | null
  >(null);

  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-900/[0.03] sm:p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
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
            <h2 className="text-lg font-semibold text-slate-900">
              Sources
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Information retrieved from your document
            </p>
          </div>
        </div>

        <span className="inline-flex w-fit items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
          {sources.length}{" "}
          {sources.length === 1 ? "source" : "sources"}
        </span>
      </div>

      {/* Source List */}
      <div className="mt-6 space-y-3">
        {sources.map((source, index) => {
          const isExpanded = expandedSource === index;

          return (
            <div
              key={`${source.document_id}-${source.chunk_index}`}
              className={`overflow-hidden rounded-2xl border transition-colors duration-200 ${
                isExpanded
                  ? "border-indigo-200 bg-indigo-50/30"
                  : "border-slate-200 bg-slate-50/60 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              {/* Source Header */}
              <button
                type="button"
                aria-expanded={isExpanded}
                onClick={() =>
                  setExpandedSource(isExpanded ? null : index)
                }
                className="flex w-full items-center justify-between gap-4 p-4 text-left sm:p-5"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold transition-colors ${
                      isExpanded
                        ? "bg-indigo-600 text-white"
                        : "border border-slate-200 bg-white text-indigo-600 shadow-sm"
                    }`}
                  >
                    {String(index + 1).padStart(2, "0")}
                  </div>

                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-800">
                      Document {source.document_id}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Chunk {source.chunk_index}
                    </p>
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-3">
                  <span className="rounded-lg border border-emerald-100 bg-emerald-50 px-2.5 py-1.5 text-xs font-semibold text-emerald-700">
                    {(source.similarity * 100).toFixed(1)}% match
                  </span>

                  <span
                    className={`flex h-7 w-7 items-center justify-center rounded-lg transition-all duration-200 ${
                      isExpanded
                        ? "rotate-180 bg-indigo-100 text-indigo-600"
                        : "bg-white text-slate-400"
                    }`}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className="h-4 w-4"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m6 9 6 6 6-6"
                      />
                    </svg>
                  </span>
                </div>
              </button>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="border-t border-slate-200/80 px-4 pb-5 pt-4 sm:px-5">
                  <div className="mb-3 flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Retrieved passage
                    </p>
                  </div>

                  <div className="rounded-xl border border-slate-200/70 bg-white p-4">
                    <p className="whitespace-pre-wrap break-words text-sm leading-7 text-slate-600">
                      {source.content}
                    </p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}