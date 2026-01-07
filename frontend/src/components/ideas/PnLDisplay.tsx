import { clsx } from 'clsx';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface PnLDisplayProps {
  pnlPercent: number | null;
  pnlAbsolute?: number | null;
  isRealized?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export function PnLDisplay({
  pnlPercent,
  pnlAbsolute,
  isRealized = false,
  size = 'md',
  showIcon = true,
}: PnLDisplayProps) {
  if (pnlPercent === null || pnlPercent === undefined) {
    return <span className="text-gray-400">--</span>;
  }

  const pnlValue = Number(pnlPercent);
  const isPositive = pnlValue >= 0;
  const Icon = isPositive ? TrendingUp : TrendingDown;

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl font-semibold',
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  const formatPercent = (value: number) => {
    const formatted = (Number(value) * 100).toFixed(2);
    return isPositive ? `+${formatted}%` : `${formatted}%`;
  };

  const formatAbsolute = (value: number) => {
    const numValue = Number(value);
    const formatted = Math.abs(numValue).toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
    return numValue >= 0 ? `+${formatted}` : `-${formatted}`;
  };

  return (
    <div className="flex items-center gap-2">
      {showIcon && (
        <Icon
          className={clsx(
            iconSizes[size],
            isPositive ? 'text-green-600' : 'text-red-600'
          )}
        />
      )}
      <span
        className={clsx(
          sizeClasses[size],
          isPositive ? 'text-green-600' : 'text-red-600'
        )}
      >
        {formatPercent(pnlValue)}
      </span>
      {pnlAbsolute !== undefined && pnlAbsolute !== null && (
        <span
          className={clsx(
            'text-sm',
            isPositive ? 'text-green-600' : 'text-red-600'
          )}
        >
          ({formatAbsolute(pnlAbsolute)})
        </span>
      )}
      {isRealized && (
        <span className="badge-gray text-xs">Realized</span>
      )}
    </div>
  );
}
