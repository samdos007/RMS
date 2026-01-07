import { clsx } from 'clsx';
import type { IdeaStatus } from '../../types';

interface StatusBadgeProps {
  status: IdeaStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig: Record<IdeaStatus, { label: string; className: string }> = {
    DRAFT: { label: 'Draft', className: 'badge-gray' },
    ACTIVE: { label: 'Active', className: 'badge-green' },
    SCALED_UP: { label: 'Scaled Up', className: 'badge-blue' },
    TRIMMED: { label: 'Trimmed', className: 'badge-yellow' },
    CLOSED: { label: 'Closed', className: 'badge-gray' },
    KILLED: { label: 'Killed', className: 'badge-red' },
  };

  const config = statusConfig[status];

  return <span className={clsx(config.className)}>{config.label}</span>;
}
