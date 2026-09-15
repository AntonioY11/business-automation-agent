import { Suspense } from "react";
import { connection } from "next/server";
import Link from "next/link";

import { getApprovals } from "@/lib/api";
import ApprovalActions from "@/components/ApprovalActions";
import StatusBadge from "@/components/StatusBadge";
import TableSkeleton from "@/components/TableSkeleton";

async function ApprovalsTable() {
  await connection();

  const approvals = await getApprovals();

  if (approvals.length === 0) {
    return (
      <div className="p-6 text-sm text-zinc-500">
        No approvals found.
      </div>
    );
  }

  return (
    <table className="w-full">
      <thead className="border-b border-zinc-200 bg-zinc-50">
        <tr>
          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Approval
          </th>

          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Intent
          </th>

          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Account
          </th>

          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Status
          </th>

          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Created
          </th>

          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Actions
          </th>
        </tr>
      </thead>

      <tbody className="divide-y divide-zinc-200">
        {approvals.map((approval) => (
          <tr key={approval.id} className="hover:bg-zinc-50">
            <td className="px-6 py-4">
              <p className="font-medium text-zinc-900">
                Approval #{approval.id}
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Customer #{approval.customer_id}
                {approval.request_id !== null && (
                  <>
                    {" · "}
                    <Link
                      href={`/requests/${approval.request_id}`}
                      className="underline"
                    >
                      Request #{approval.request_id}
                    </Link>
                  </>
                )}
              </p>
            </td>

            <td className="px-6 py-4 text-sm text-zinc-600">
              {approval.intent}
            </td>

            <td className="px-6 py-4 text-sm text-zinc-600">
              {approval.account_id ?? "—"}
            </td>

            <td className="px-6 py-4">
              <StatusBadge status={approval.status} />
            </td>

            <td className="px-6 py-4 text-sm text-zinc-600">
              {new Date(approval.created_at).toLocaleString()}
            </td>

            <td className="px-6 py-4">
              {approval.status === "pending" ? (
                <ApprovalActions approvalId={approval.id} />
              ) : (
                <span className="text-sm text-zinc-400">
                  No actions
                </span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function ApprovalsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <p className="text-sm text-zinc-500">
          Human review
        </p>

        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          Approvals
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          Review and manage actions that require human approval.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <Suspense fallback={<TableSkeleton />}>
          <ApprovalsTable />
        </Suspense>
      </div>
    </div>
  );
}
