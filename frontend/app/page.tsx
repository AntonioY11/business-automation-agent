import { Suspense } from "react";
import { connection } from "next/server";

import StatCard from "@/components/StatCard";
import StatusBadge from "@/components/StatusBadge";
import TableSkeleton from "@/components/TableSkeleton";
import { getRequests, getApprovals } from "@/lib/api";

function OverviewSkeleton() {
  return (
    <>
      <section className="grid gap-4 md:grid-cols-4">
        {[0, 1, 2, 3].map((card) => (
          <div
            key={card}
            className="rounded-xl border border-zinc-200 bg-white p-6"
          >
            <div className="h-4 w-28 animate-pulse rounded bg-zinc-200" />

            <div className="mt-3 h-8 w-12 animate-pulse rounded bg-zinc-200" />
          </div>
        ))}
      </section>

      <section className="mt-8 rounded-xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-200 p-6">
          <h3 className="font-semibold text-zinc-900">
            Recent Requests
          </h3>
        </div>

        <TableSkeleton />
      </section>
    </>
  );
}

async function Overview() {
  await connection();

  const [requests, approvals] = await Promise.all([
    getRequests(),
    getApprovals(),
  ]);

  const countByStatus = (status: string) =>
    requests.filter((request) => request.status === status).length;

  const pendingApprovals = approvals.filter(
    (approval) => approval.status === "pending"
  ).length;

  return (
    <>
      <section className="grid gap-4 md:grid-cols-4">
        <StatCard
          label="Pending Requests"
          value={countByStatus("pending")}
        />

        <StatCard
          label="Completed"
          value={countByStatus("completed")}
        />

        <StatCard
          label="Failed"
          value={countByStatus("failed")}
        />

        <StatCard
          label="Pending Approvals"
          value={pendingApprovals}
        />
      </section>

      <section className="mt-8 rounded-xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-200 p-6">
          <h3 className="font-semibold text-zinc-900">
            Recent Requests
          </h3>
        </div>

        {requests.length === 0 ? (
          <div className="p-6 text-sm text-zinc-500">
            No requests yet.
          </div>
        ) : (
          <div className="divide-y divide-zinc-200">
            {requests.slice(0, 5).map((request) => (
              <div
                key={request.id}
                className="flex items-center justify-between p-6"
              >
                <div>
                  <p className="font-medium text-zinc-900">
                    {request.intent ?? "Processing request"}
                  </p>

                  <p className="mt-1 text-sm text-zinc-500">
                    Customer #{request.customer_id}
                  </p>
                </div>

                <StatusBadge status={request.status} />
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

export default function Home() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-zinc-900">
          Dashboard
        </h2>

        <p className="mt-1 text-zinc-500">
          Overview of your business automation activity.
        </p>
      </div>

      <Suspense fallback={<OverviewSkeleton />}>
        <Overview />
      </Suspense>
    </div>
  );
}
