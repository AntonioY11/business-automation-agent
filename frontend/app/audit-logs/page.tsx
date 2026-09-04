import { getAuditLogs, AuditLog } from "@/lib/api";

export default async function AuditLogsPage() {
  let logs: AuditLog[] = [];

  try {
    logs = await getAuditLogs();
  } catch {
    logs = [];
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <p className="text-sm text-zinc-500">
          System activity
        </p>

        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          Audit Logs
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          Track important actions and events across the system.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        {logs.length === 0 ? (
          <div className="p-6 text-sm text-zinc-500">
            No audit logs found.
          </div>
        ) : (
          <table className="w-full">
            <thead className="border-b border-zinc-200 bg-zinc-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                  Event
                </th>

                <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                  Customer
                </th>

                <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                  Details
                </th>

                <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                  Created
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-zinc-200">
              {logs.map((log) => (
                <tr
                  key={log.id}
                  className="hover:bg-zinc-50"
                >
                  <td className="px-6 py-4">
                    <p className="font-medium text-zinc-900">
                      {log.event_type}
                    </p>

                    <p className="mt-1 text-sm text-zinc-500">
                      Log #{log.id}
                    </p>
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {log.customer_id
                      ? `Customer #${log.customer_id}`
                      : "System"}
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {log.details ?? "—"}
                  </td>

                  <td className="px-6 py-4 text-sm text-zinc-600">
                    {new Date(log.created_at).toLocaleString()}
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