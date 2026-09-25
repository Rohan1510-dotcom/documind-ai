type AnswerCardProps = {
  answer: string;
};

export default function AnswerCard({
  answer,
}: AnswerCardProps) {
  return (
    <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black text-sm text-white">
          AI
        </div>

        <div>
          <h2 className="font-semibold">
            DocuMind AI
          </h2>

          <p className="text-xs text-gray-400">
            Generated from your document
          </p>
        </div>
      </div>

      <div className="mt-5 border-t pt-5">
        <p className="whitespace-pre-wrap leading-7 text-gray-700">
          {answer}
        </p>
      </div>
    </div>
  );
}