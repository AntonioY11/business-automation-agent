import StatCard from "@/components/StatCard";
import { getRequests,getApprovals } from "@/lib/api";

export default async function Home() {
  const [requests, approvals] = await Promise.all([
    getRequests(),
    getApprovals(),
  ]);

  const pendingRequests = requests.filter(
    (request) => request.status === "pending"
  ).length;

  const completedRequests = requests.filter(
    (request) => request.status === "completed"
  ).length;

  const failedRequests = requests.filter(
    (request) => request.status === "failed"
  ).length;

  const pendingApprovals = approvals.filter(
  (approval) => approval.status === "pending"
  ).length;

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

      <section className="grid gap-4 md:grid-cols-4">
        <StatCard
          label="Pending Requests"
          value={pendingRequests}
        />

        <StatCard
          label="Completed"
          value={completedRequests}
        />

        <StatCard
          label="Failed"
          value={failedRequests}
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

              <span className="rounded-full bg-zinc-100 px-3 py-1 text-sm font-medium text-zinc-700">
                {request.status}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}