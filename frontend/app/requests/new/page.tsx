"use client";

import { useState } from "react";
import { createRequest } from "@/lib/api";

export default function NewRequestPage() {
  const [customerId, setCustomerId] = useState("");
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const data = await createRequest(
            Number(customerId),
            request
            );

            setResult(data);
        } catch {
            setError("Failed to process request.");
        } finally {
            setLoading(false);
        }
    }

  return (
    <div className="p-8">
      <div className="mb-8">
        <p className="text-sm text-zinc-500">
          AI automation
        </p>

        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          New Request
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          Submit a business request for the AI agent to process.
        </p>
      </div>

      <div className="max-w-2xl rounded-xl border border-zinc-200 bg-white p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="customerId"
              className="block text-sm font-medium text-zinc-700"
            >
              Customer ID
            </label>

            <input
              id="customerId"
              type="number"
              value={customerId}
              onChange={(event) => setCustomerId(event.target.value)}
              placeholder="e.g. 1"
              className="mt-2 w-full rounded-lg border border-zinc-300 px-4 py-2.5 text-sm outline-none focus:border-zinc-500"
              required
            />
          </div>

          <div>
            <label
              htmlFor="request"
              className="block text-sm font-medium text-zinc-700"
            >
              Business Request
            </label>

            <textarea
              id="request"
              value={request}
              onChange={(event) => setRequest(event.target.value)}
              placeholder="e.g. Please cancel my subscription for account ACC-001."
              rows={6}
              className="mt-2 w-full resize-none rounded-lg border border-zinc-300 px-4 py-3 text-sm outline-none focus:border-zinc-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
            {loading ? "Processing..." : "Process Request"}
          </button>
        </form>
        {error && (
            <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
                <p className="text-sm text-red-700">
                {error}
                </p>
            </div>
            )}

            {result && (
            <div className="mt-6 rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                <h2 className="font-semibold text-zinc-900">
                Request Processed
                </h2>

                <p className="mt-2 text-sm text-zinc-600">
                {result.customer_message}
                </p>
            </div>
        )}
      </div>
    </div>
  );
}