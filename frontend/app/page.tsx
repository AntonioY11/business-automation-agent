import StatCard from "@/components/StatCard";

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

      <section className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Pending Requests"
          value={3}
        />

        <StatCard
          label="Completed"
          value={24}
        />

        <StatCard
          label="Failed"
          value={2}
        />
      </section>

      <section className="mt-8 rounded-xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-200 p-6">
          <h3 className="font-semibold text-zinc-900">
            Recent Requests
          </h3>
        </div>

        <div className="divide-y divide-zinc-200">
          <div className="flex items-center justify-between p-6">
            <div>
              <p className="font-medium text-zinc-900">
                Cancel subscription
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Customer request
              </p>
            </div>

            <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
              Completed
            </span>
          </div>

          <div className="flex items-center justify-between p-6">
            <div>
              <p className="font-medium text-zinc-900">
                Change address
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Customer request
              </p>
            </div>

            <span className="rounded-full bg-yellow-100 px-3 py-1 text-sm font-medium text-yellow-700">
              Pending
            </span>
          </div>

          <div className="flex items-center justify-between p-6">
            <div>
              <p className="font-medium text-zinc-900">
                Refund request
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Customer request
              </p>
            </div>

            <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
              Approval
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}