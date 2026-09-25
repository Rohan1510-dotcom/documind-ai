
type DocumentCardProps = {
  filename: string;
  documentId: number;
  onDelete: (documentId: number) => void;
};

export default function DocumentCard({
  filename,
  documentId,
  onDelete,
}: DocumentCardProps) {
  return (
    <div className="mt-6 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-900/[0.03] sm:p-5">
      <div className="flex min-w-0 flex-col gap-4 sm:flex-row sm:items-center">
        {/* Document Icon */}
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            className="h-7 w-7"
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

        {/* Document Details */}
        <div className="min-w-0 flex-1">
          <p className="break-all text-sm font-semibold leading-6 text-slate-800 sm:text-base">
            {filename}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Document ID: {documentId}
          </p>

          <p className="mt-2 text-xs font-medium text-slate-400">
            PDF document
          </p>
        </div>

        {/* Status and Delete */}
        <div className="flex shrink-0 items-center gap-3">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Ready
          </div>

          <button
            type="button"
            onClick={() => onDelete(documentId)}
            aria-label={`Delete ${filename}`}
            title="Delete document"
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-red-100 bg-red-50 text-red-500 transition hover:border-red-200 hover:bg-red-100 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-300"
          >
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
                d="M3 6h18M8 6V4h8v2m-10 0 1 14h10l1-14M10 10v6m4-6v6"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}