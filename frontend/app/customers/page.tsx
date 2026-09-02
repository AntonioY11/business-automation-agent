import Link from "next/link";
import { getCustomers } from "@/lib/api";

export default async function CustomersPage() {
  const customers = await getCustomers();

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-zinc-900">
          Customers
        </h1>

        <p className="mt-1 text-zinc-500">
          View and manage your customers.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <table className="w-full">
          <thead className="border-b border-zinc-200 bg-zinc-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                Customer
              </th>

              <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                Email
              </th>

              <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                Subscription
              </th>

              <th className="px-6 py-4 text-left text-sm font-medium text-zinc-500">
                Address
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-zinc-200">
            {customers.map((customer) => (
              <tr
                key={customer.id}
                className="hover:bg-zinc-50"
              >
                <td className="px-6 py-4">
                  <Link
                    href={`/customers/${customer.id}`}
                    className="block"
                  >
                    <p className="font-medium text-zinc-900">
                      {customer.name}
                    </p>

                    <p className="mt-1 text-sm text-zinc-500">
                      Customer #{customer.id}
                    </p>
                  </Link>
                </td>

                <td className="px-6 py-4 text-sm text-zinc-600">
                  {customer.email}
                </td>

                <td className="px-6 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                    {customer.subscription_status}
                  </span>
                </td>

                <td className="px-6 py-4 text-sm text-zinc-600">
                  {customer.address ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}