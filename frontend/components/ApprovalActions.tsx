"use client";

import { useState } from "react";
import {
  approveApproval,
  rejectApproval,
} from "@/lib/api";

type ApprovalActionsProps = {
  approvalId: number;
};

export default function ApprovalActions({
  approvalId,
}: ApprovalActionsProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleApprove() {
    setLoading(true);
    setError("");

    try {
      await approveApproval(approvalId);
      window.location.reload();
    } catch {
      setError("Failed to approve approval.");
      setLoading(false);
    }
  }

  async function handleReject() {
    setLoading(true);
    setError("");

    try {
      await rejectApproval(approvalId);
      window.location.reload();
    } catch {
      setError("Failed to reject approval.");
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
          onClick={handleApprove}
          disabled={loading}
          className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Processing..." : "Approve"}
        </button>

        <button
          onClick={handleReject}
          disabled={loading}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}