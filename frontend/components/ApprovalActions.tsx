"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import {
  ApprovalActionResult,
  approveApproval,
  rejectApproval,
} from "@/lib/api";

type ApprovalActionsProps = {
  approvalId: number;
};

export default function ApprovalActions({
  approvalId,
}: ApprovalActionsProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const busy = loading || isPending;

  async function run(action: (id: number) => Promise<ApprovalActionResult>) {
    setLoading(true);
    setError("");

    try {
      const result = await action(approvalId);

      if (!result.success) {
        setError(result.message);
      }

      startTransition(() => {
        router.refresh();
      });
    } catch (actionError) {
      setError(
        actionError instanceof Error
          ? actionError.message
          : "Something went wrong."
      );
      startTransition(() => {
        router.refresh();
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {error && (
        <p className="mb-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => run(approveApproval)}
          disabled={busy}
          className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "Processing..." : "Approve"}
        </button>

        <button
          onClick={() => run(rejectApproval)}
          disabled={busy}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
