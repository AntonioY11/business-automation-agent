import { getApprovals, Approval } from "@/lib/api";

function getStatusClass(status: string) {
  switch (status) {
    case "pending":
      return "bg-yellow-100 text-yellow-700";
    case "approved":
      return "bg-green-100 text-green-700";
    case "rejected":
      return "bg-red-100 text-red-700";
    default:
      return "bg-zinc-100 text-zinc-700";
  }
}

export default async function ApprovalsPage() {
  let approvals: Approval[] = [];

  try {
    approvals = await getApprovals();
  } catch {
    approvals = [];
  }

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
        {approvals.length === 0 ? (
          <div className="p-6 text-sm text-zinc-500">
            No approvals found.
          </div>
        ) : (
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
              </tr>
            </thead>

            <tbody className="divide-y divide-zinc-200">
              {approvals.map((approval) => (
                <tr
                  key={approval.id}
                  className="hover:bg-zinc-50"
                >
                  <td className="px-6 py-4">
                    <p className="font-medium text-zinc-900">
                      Approval #{approval.id}
                    </p>

                    <p className="mt-1 text-sm text-zinc-500">
                      Customer #{approval.customer_id}
                    </p>
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {approval.intent}
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {approval.account_id ?? "—"}
                  </td>

                  <td className="px-6 py-4">
                    <span
                      className={`rounded-full px-3 py-1 text-sm font-medium ${getStatusClass(
                        approval.status
                      )}`}
                    >
                      {approval.status}
                    </span>
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {new Date(approval.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}