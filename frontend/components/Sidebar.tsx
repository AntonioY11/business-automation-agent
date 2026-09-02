export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-zinc-200 bg-white p-6">
      <div className="mb-10">
        <h1 className="text-xl font-bold text-zinc-900">
          AI Automation
        </h1>

        <p className="mt-1 text-sm text-zinc-500">
          Business Operations
        </p>
      </div>

      <nav className="space-y-2">
        <a
          href="#"
          className="block rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white"
        >
          Dashboard
        </a>

        <a
          href="/requests"
          className="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100"
        >
          Requests
        </a>

        <a
          href="/customers"
          className="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100"
        >
          Customers
        </a>

        <a
          href="#"
          className="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100"
        >
          Approvals
        </a>

        <a
          href="#"
          className="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100"
        >
          Audit Logs
        </a>
      </nav>
    </aside>
  );
}