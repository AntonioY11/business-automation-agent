type StatCardProps = {
  label: string;
  value: number;
};

export default function StatCard({
  label,
  value,
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6">
      <p className="text-sm font-medium text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-bold text-zinc-900">
        {value}
      </p>
    </div>
  );
}