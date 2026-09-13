const STATUS_STYLES: Record<string, string> = {
  completed: "bg-green-100 text-green-700",
  approved: "bg-green-100 text-green-700",
  success: "bg-green-100 text-green-700",
  active: "bg-green-100 text-green-700",
  pending: "bg-yellow-100 text-yellow-700",
  processing: "bg-blue-100 text-blue-700",
  failed: "bg-red-100 text-red-700",
  rejected: "bg-red-100 text-red-700",
  cancelled: "bg-zinc-200 text-zinc-700",
};

const FALLBACK_STYLE = "bg-zinc-100 text-zinc-700";

type StatusBadgeProps = {
  status: string;
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const style = STATUS_STYLES[status] ?? FALLBACK_STYLE;

  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${style}`}
    >
      {status}
    </span>
  );
}
