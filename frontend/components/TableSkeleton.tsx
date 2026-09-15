type TableSkeletonProps = {
  rows?: number;
};

export default function TableSkeleton({ rows = 5 }: TableSkeletonProps) {
  return (
    <div className="divide-y divide-zinc-200">
      {Array.from({ length: rows }, (_, row) => (
        <div
          key={row}
          className="flex items-center justify-between px-6 py-5"
        >
          <div className="w-1/2 space-y-2">
            <div className="h-4 w-3/4 animate-pulse rounded bg-zinc-200" />

            <div className="h-3 w-24 animate-pulse rounded bg-zinc-200" />
          </div>

          <div className="h-6 w-20 animate-pulse rounded-full bg-zinc-200" />
        </div>
      ))}
    </div>
  );
}
