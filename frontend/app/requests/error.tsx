"use client";

import { useEffect } from "react";

export default function Error({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-zinc-900">
          Requests
        </h1>
      </div>

      <div className="max-w-2xl rounded-xl border border-red-200 bg-red-50 p-6">
        <h2 className="font-semibold text-red-800">
          Could not load requests
        </h2>

        <p className="mt-2 text-sm text-red-700">
          The API did not respond. Check that the backend is running,
          then try again.
        </p>

        {error.digest && (
          <p className="mt-2 font-mono text-xs text-red-600">
            Reference: {error.digest}
          </p>
        )}

        <button
          onClick={() => retry()}
          className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
