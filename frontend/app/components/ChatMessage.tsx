
"use client";

type ChatMessageProps = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatMessage({
  role,
  content,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`flex max-w-[90%] items-start gap-3 sm:max-w-[80%] ${
          isUser ? "flex-row-reverse" : "flex-row"
        }`}
      >
        {/* Avatar */}
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
            isUser
              ? "bg-indigo-600 text-white"
              : "border border-slate-200 bg-white text-indigo-600 shadow-sm"
          }`}
        >
          {isUser ? (
            "You"
          ) : (
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
                d="M12 3v3m0 12v3M3 12h3m12 0h3M5.64 5.64l2.12 2.12m8.48 8.48 2.12 2.12m0-12.72-2.12 2.12m-8.48 8.48-2.12 2.12"
              />
              <circle cx="12" cy="12" r="4" />
            </svg>
          )}
        </div>

        {/* Message */}
        <div
          className={`min-w-0 rounded-2xl px-4 py-3.5 sm:px-5 ${
            isUser
              ? "rounded-tr-md bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
              : "rounded-tl-md border border-slate-200/80 bg-white text-slate-800 shadow-sm shadow-slate-900/[0.03]"
          }`}
        >
          <p
            className={`mb-2 text-xs font-semibold ${
              isUser ? "text-indigo-100" : "text-indigo-600"
            }`}
          >
            {isUser ? "You" : "DocuMind AI"}
          </p>

          <p className="whitespace-pre-wrap break-words text-sm leading-7">
            {content}
          </p>
        </div>
      </div>
    </div>
  );
}