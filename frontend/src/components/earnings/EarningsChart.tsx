import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { Earnings } from '../../types';

interface EarningsChartProps {
  earnings: Earnings[];
  metric: 'eps' | 'rev';
  tickers: string[];
}

export function EarningsChart({ earnings, metric, tickers }: EarningsChartProps) {
  // Group by fiscal quarter
  const quarters = Array.from(new Set(earnings.map((e) => e.fiscal_quarter))).sort();

  const data = quarters.map((quarter) => {
    const quarterData: Record<string, string | number | null> = { quarter };

    tickers.forEach((ticker) => {
      const e = earnings.find(
        (e) => e.fiscal_quarter === quarter && e.ticker === ticker
      );

      if (metric === 'eps') {
        quarterData[`${ticker}_est`] = e?.estimate_eps ?? null;
        quarterData[`${ticker}_act`] = e?.actual_eps ?? null;
      } else {
        // Revenue in billions
        quarterData[`${ticker}_est`] = e?.estimate_rev
          ? e.estimate_rev / 1e9
          : null;
        quarterData[`${ticker}_act`] = e?.actual_rev ? e.actual_rev / 1e9 : null;
      }
    });

    return quarterData;
  });

  const colors = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b'];

  return (
    <div className="card p-4">
      <h3 className="mb-4 text-lg font-medium text-gray-900">
        {metric === 'eps' ? 'EPS' : 'Revenue'} - Estimate vs Actual
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="quarter" tick={{ fontSize: 12 }} />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(value) =>
              metric === 'rev' ? `$${value}B` : value.toFixed(2)
            }
          />
          <Tooltip
            formatter={(value: number) =>
              metric === 'rev'
                ? `$${value?.toFixed(2)}B`
                : value?.toFixed(2) ?? '-'
            }
          />
          <Legend />

          {tickers.map((ticker, index) => (
            <Line
              key={`${ticker}_est`}
              type="monotone"
              dataKey={`${ticker}_est`}
              name={`${ticker} Est`}
              stroke={colors[index % colors.length]}
              strokeDasharray="5 5"
              dot={{ r: 4 }}
              connectNulls
            />
          ))}

          {tickers.map((ticker, index) => (
            <Line
              key={`${ticker}_act`}
              type="monotone"
              dataKey={`${ticker}_act`}
              name={`${ticker} Act`}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={{ r: 5 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
