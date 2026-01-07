import { useQuery } from '@tanstack/react-query';
import { RefreshCw } from 'lucide-react';
import { foldersApi } from '../../api/folders';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import type { ThemeTickerPerformance } from '../../types';

interface ThemePerformanceProps {
  folderId: string;
  themeDate: string;
}

export function ThemePerformance({ folderId, themeDate }: ThemePerformanceProps) {
  const { data: performance, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['theme-performance', folderId],
    queryFn: () => foldersApi.getThemePerformance(folderId),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!performance || performance.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
        <p className="text-gray-500">No tickers in this theme</p>
      </div>
    );
  }

  // Format currency
  const formatPrice = (price: number | null) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${price.toFixed(2)}`;
  };

  // Format percentage
  const formatPnL = (pnl: number | null) => {
    if (pnl === null || pnl === undefined) return 'N/A';
    const sign = pnl >= 0 ? '+' : '';
    return `${sign}${pnl.toFixed(2)}%`;
  };

  // Get color class for P&L
  const getPnLColor = (pnl: number | null) => {
    if (pnl === null || pnl === undefined) return 'text-gray-500';
    return pnl >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">
            Performance since{' '}
            {new Date(themeDate).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh Prices
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Ticker
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                Start Price
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                Current Price
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                P&L
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {performance.map((ticker: ThemeTickerPerformance) => (
              <tr key={ticker.ticker} className="hover:bg-gray-50">
                <td className="whitespace-nowrap px-6 py-4">
                  <span className="font-semibold text-gray-900">{ticker.ticker}</span>
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-right text-sm text-gray-900">
                  {formatPrice(ticker.start_price)}
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-right text-sm text-gray-900">
                  {formatPrice(ticker.current_price)}
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-right">
                  <span className={`text-sm font-semibold ${getPnLColor(ticker.pnl_percent)}`}>
                    {formatPnL(ticker.pnl_percent)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary stats */}
      {performance.length > 0 && (
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="card p-4">
            <p className="text-sm text-gray-500">Total Tickers</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">{performance.length}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-500">Avg P&L</p>
            <p className={`mt-1 text-2xl font-semibold ${getPnLColor(calculateAvgPnL(performance))}`}>
              {formatPnL(calculateAvgPnL(performance))}
            </p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-500">Best Performer</p>
            <p className="mt-1 text-lg font-semibold text-green-600">
              {getBestPerformer(performance)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper to calculate average P&L
function calculateAvgPnL(performance: ThemeTickerPerformance[]): number | null {
  const validPnLs = performance
    .map((t) => t.pnl_percent)
    .filter((pnl): pnl is number => pnl !== null && pnl !== undefined);

  if (validPnLs.length === 0) return null;

  const sum = validPnLs.reduce((acc, pnl) => acc + pnl, 0);
  return sum / validPnLs.length;
}

// Helper to get best performer
function getBestPerformer(performance: ThemeTickerPerformance[]): string {
  const validTickers = performance.filter(
    (t) => t.pnl_percent !== null && t.pnl_percent !== undefined
  );

  if (validTickers.length === 0) return 'N/A';

  const best = validTickers.reduce((prev, current) =>
    (current.pnl_percent ?? -Infinity) > (prev.pnl_percent ?? -Infinity) ? current : prev
  );

  return `${best.ticker} (${best.pnl_percent! >= 0 ? '+' : ''}${best.pnl_percent!.toFixed(2)}%)`;
}
