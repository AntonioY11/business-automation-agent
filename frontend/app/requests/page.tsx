import { Suspense } from "react";
import { connection } from "next/server";
import Link from "next/link";

import { getRequests, Request } from "@/lib/api";

function getPriorityClass(priority: string | null) {
  switch (priority) {
    case "high":
      return "bg-red-100 text-red-700";

    case "low":
      return "bg-blue-100 text-blue-700";

    case "normal":
      return "bg-zinc-100 text-zinc-700";

    default:
      return "bg-zinc-100 text-zinc-700";
  }
}

function TableSkeleton() {
  return (
    <div className="divide-y divide-zinc-200">
      {[0, 1, 2, 3, 4].map((row) => (
        <div
          key={row}
          className="flex items-center justify-between px-6 py-5"
        >
          <div className="w-1/2 space-y-2">
            <div className="h-4 w-3/4 animate-pulse rounded bg-zinc-200" />

            <div className="h-3 w-24 animate-pulse rounded bg-zinc-200" />
          </div>

          <div className="h-6 w-20 animate-pulse rounded-full bg-zinc-200" />
        </div>
      ))}
    </div>
  );
}

async function RequestsTable() {
  await connection();

  const requests: Request[] = await getRequests();

  if (requests.length === 0) {
    return (
      <div className="p-6 text-sm text-zinc-500">
        No requests yet.
      </div>
    );
  }

  return (
    <table className="w-full">
      <thead className="border-b border-zinc-200 bg-zinc-50">
        <tr>
          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Request
          </th>
          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Intent
          </th>
          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Priority
          </th>
          <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
            Status
          </th>
        </tr>
      </thead>

      <tbody className="divide-y divide-zinc-200">
        {requests.map((request) => (
          <tr key={request.id} className="cursor-pointer hover:bg-zinc-50">
            <td className="px-6 py-4">
              <Link
                href={`/requests/${request.id}`}
                className="block"
              >
                <p className="font-medium text-zinc-900">
                  {request.raw_text}
                </p>

                <p className="mt-1 text-sm text-zinc-500">
                  Request #{request.id}
                </p>
              </Link>
            </td>

            <td className="px-6 py-4 text-sm text-zinc-600">
              {request.intent ?? "—"}
            </td>

            <td className="px-6 py-4">
              <span className={`rounded-full px-3 py-1 text-sm ${getPriorityClass(request.priority)}`}>
                {request.priority ?? "—"}
              </span>
            </td>

            <td className="px-6 py-4">
              <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                {request.status}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function RequestsPage() {
  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">
            Requests
          </h1>

          <p className="mt-1 text-zinc-500">
            View and manage customer requests.
          </p>
        </div>

        <Link
          href="/requests/new"
          className="rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-zinc-800"
        >
          New Request
        </Link>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <Suspense fallback={<TableSkeleton />}>
          <RequestsTable />
        </Suspense>
      </div>
    </div>
  );
}
