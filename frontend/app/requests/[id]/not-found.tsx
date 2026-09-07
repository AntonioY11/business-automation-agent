import Link from "next/link";

export default function NotFound() {
  return (
    <div className="p-8">
      <div className="max-w-2xl rounded-xl border border-zinc-200 bg-white p-6">
        <h1 className="text-xl font-bold text-zinc-900">
          Request not found
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          This request does not exist, or it may have been removed.
        </p>

        <Link
          href="/requests"
          className="mt-4 inline-block rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
        >
          Back to requests
        </Link>
      </div>
    </div>
  );
}
