import { Suspense } from "react";
import { connection } from "next/server";
import Link from "next/link";

import { getCustomers } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";
import TableSkeleton from "@/components/TableSkeleton";

async function CustomersTable() {
  await connection();

  const customers = await getCustomers();

  if (customers.length === 0) {
    return (
      <div className="p-6 text-sm text-zinc-500">
        No customers yet.
      </div>
    );
  }

  return (
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
          <tr key={customer.id} className="hover:bg-zinc-50">
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
              <StatusBadge status={customer.subscription_status} />
            </td>

            <td className="px-6 py-4 text-sm text-zinc-600">
              {customer.address ?? "—"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function CustomersPage() {
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
        <Suspense fallback={<TableSkeleton />}>
          <CustomersTable />
        </Suspense>
      </div>
    </div>
  );
}
