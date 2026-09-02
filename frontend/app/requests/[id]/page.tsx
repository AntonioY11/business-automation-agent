import { getRequest } from "@/lib/api";

type RequestDetailsPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function RequestDetailsPage({
  params,
}: RequestDetailsPageProps) {
  const { id } = await params;
  const request = await getRequest(Number(id));

  return (
    <div className="p-8">
      <div className="mb-8">
        <p className="text-sm text-zinc-500">
          Request #{request.id}
        </p>

        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          Request Details
        </h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 font-semibold text-zinc-900">
            Request
          </h2>

          <p className="text-zinc-700">
            {request.raw_text}
          </p>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 font-semibold text-zinc-900">
            Information
          </h2>

          <div className="space-y-3 text-sm">
            <p>
              <span className="font-medium text-zinc-500">
                Intent:
              </span>{" "}
              {request.intent ?? "—"}
            </p>

            <p>
              <span className="font-medium text-zinc-500">
                Priority:
              </span>{" "}
              {request.priority ?? "—"}
            </p>

            <p>
              <span className="font-medium text-zinc-500">
                Status:
              </span>{" "}
              {request.status}
            </p>

            <p>
              <span className="font-medium text-zinc-500">
                Customer ID:
              </span>{" "}
              {request.customer_id}
            </p>

            <p>
              <span className="font-medium text-zinc-500">
                Account ID:
              </span>{" "}
              {request.account_id ?? "—"}
            </p>

            <p>
              <span className="font-medium text-zinc-500">
                Created:
              </span>{" "}
              {new Date(request.created_at).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {request.error_message && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="font-semibold text-red-800">
            Error
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {request.error_message}
          </p>
        </div>
      )}
    </div>
  );
}