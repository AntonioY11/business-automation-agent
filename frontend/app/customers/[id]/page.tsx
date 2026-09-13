import Link from "next/link";
import {
  getCustomer,
  getCustomerRequests,
} from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

type CustomerDetailsPageProps = {
  params: Promise<{
    id: string;
  }>;
};

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

export default async function CustomerDetailsPage({
  params,
}: CustomerDetailsPageProps) {
  const { id } = await params;
  const customerId = Number(id);

  const customer = await getCustomer(customerId);
  const requests = await getCustomerRequests(customerId);

  return (
    <div className="p-8">
      <div className="mb-8">
        <p className="text-sm text-zinc-500">
          Customer #{customer.id}
        </p>

        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          {customer.name}
        </h1>
      </div>

      <div className="rounded-xl border border-zinc-200 bg-white p-6">
        <h2 className="mb-4 font-semibold text-zinc-900">
          Customer Information
        </h2>

        <div className="grid gap-4 text-sm md:grid-cols-2">
          <p>
            <span className="font-medium text-zinc-500">
              Name:
            </span>{" "}
            {customer.name}
          </p>

          <p>
            <span className="font-medium text-zinc-500">
              Email:
            </span>{" "}
            {customer.email}
          </p>

          <p>
            <span className="font-medium text-zinc-500">
              Subscription:
            </span>{" "}
            <StatusBadge status={customer.subscription_status} />
          </p>

          <p>
            <span className="font-medium text-zinc-500">
              Address:
            </span>{" "}
            {customer.address ?? "—"}
          </p>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-200 p-6">
          <h2 className="font-semibold text-zinc-900">
            Request History
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            {requests.length} request
            {requests.length === 1 ? "" : "s"}
          </p>
        </div>

        {requests.length === 0 ? (
          <div className="p-6 text-sm text-zinc-500">
            No requests found for this customer.
          </div>
        ) : (
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
                <tr
                  key={request.id}
                  className="hover:bg-zinc-50"
                >
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
                    <span
                      className={`rounded-full px-3 py-1 text-sm ${getPriorityClass(
                        request.priority
                      )}`}
                    >
                      {request.priority ?? "—"}
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <StatusBadge status={request.status} />
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