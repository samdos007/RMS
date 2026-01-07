import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2, Check, X } from 'lucide-react';
import { guidanceApi } from '../../api/guidance';
import { useToast } from '../ui/Toast';
import type { Guidance, GuidanceCreate, MetricType } from '../../types';

interface GuidanceTableProps {
  folderId: string;
  tickers: string[];
}

const METRIC_OPTIONS: { value: MetricType | 'OTHER'; label: string }[] = [
  { value: 'REVENUE', label: 'Revenue' },
  { value: 'EPS', label: 'EPS' },
  { value: 'EBITDA', label: 'EBITDA' },
  { value: 'FCF', label: 'Free Cash Flow' },
  { value: 'OTHER', label: 'Other' },
];

export function GuidanceTable({ folderId, tickers }: GuidanceTableProps) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const { data: guidanceData } = useQuery({
    queryKey: ['guidance', folderId],
    queryFn: () => guidanceApi.list(folderId),
  });

  const guidance = guidanceData?.guidance || [];

  const createMutation = useMutation({
    mutationFn: guidanceApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidance', folderId] });
      addToast('success', 'Guidance added');
      setShowAddForm(false);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      addToast('error', error.response?.data?.detail || 'Failed to add guidance');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<GuidanceCreate> }) =>
      guidanceApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidance', folderId] });
      addToast('success', 'Guidance updated');
      setEditingId(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: guidanceApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidance', folderId] });
      addToast('success', 'Guidance deleted');
    },
  });

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Period
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Metric
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Guidance Period
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                Guidance
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                Actual Result
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Notes
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {showAddForm && (
              <AddGuidanceRow
                folderId={folderId}
                tickers={tickers}
                onSave={(data) => createMutation.mutate(data)}
                onCancel={() => setShowAddForm(false)}
                isPending={createMutation.isPending}
              />
            )}
            {guidance.map((g) =>
              editingId === g.id ? (
                <EditGuidanceRow
                  key={g.id}
                  guidance={g}
                  onSave={(data) => updateMutation.mutate({ id: g.id, data })}
                  onCancel={() => setEditingId(null)}
                  isPending={updateMutation.isPending}
                />
              ) : (
                <GuidanceRow
                  key={g.id}
                  guidance={g}
                  onEdit={() => setEditingId(g.id)}
                  onDelete={() => {
                    if (confirm('Delete this guidance record?')) {
                      deleteMutation.mutate(g.id);
                    }
                  }}
                />
              )
            )}
            {guidance.length === 0 && !showAddForm && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-gray-500">
                  No guidance data yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="border-t bg-gray-50 px-4 py-3">
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-secondary"
          disabled={showAddForm}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Guidance
        </button>
      </div>
    </div>
  );
}

function GuidanceRow({
  guidance,
  onEdit,
  onDelete,
}: {
  guidance: Guidance;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const formatGuidance = () => {
    if (guidance.guidance_point !== null) {
      return formatMetricValue(guidance.guidance_point, guidance.metric);
    }
    if (guidance.guidance_low !== null && guidance.guidance_high !== null) {
      return `${formatMetricValue(guidance.guidance_low, guidance.metric)} - ${formatMetricValue(
        guidance.guidance_high,
        guidance.metric
      )}`;
    }
    return '-';
  };

  const getResultVsGuidance = () => {
    if (guidance.actual_result === null || guidance.vs_guidance_midpoint === null) {
      return null;
    }
    const diff = Number(guidance.vs_guidance_midpoint);
    const pct =
      guidance.guidance_midpoint !== null && guidance.guidance_midpoint !== 0
        ? (diff / Number(guidance.guidance_midpoint)) * 100
        : null;
    return { diff, pct };
  };

  const resultVsGuidance = getResultVsGuidance();

  return (
    <tr>
      <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
        {guidance.period}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
        {guidance.metric}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
        {guidance.guidance_period}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-500">
        {formatGuidance()}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-900">
        {guidance.actual_result !== null ? (
          <>
            {formatMetricValue(guidance.actual_result, guidance.metric)}
            {resultVsGuidance && resultVsGuidance.pct !== null && (
              <span
                className={`ml-1 text-xs ${
                  resultVsGuidance.diff >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                ({resultVsGuidance.diff >= 0 ? '+' : ''}
                {resultVsGuidance.pct.toFixed(1)}%)
              </span>
            )}
          </>
        ) : (
          '-'
        )}
      </td>
      <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-500">
        {guidance.notes || '-'}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm">
        <button onClick={onEdit} className="mr-2 text-gray-400 hover:text-gray-600">
          <Pencil className="h-4 w-4" />
        </button>
        <button onClick={onDelete} className="text-gray-400 hover:text-red-600">
          <Trash2 className="h-4 w-4" />
        </button>
      </td>
    </tr>
  );
}

function AddGuidanceRow({
  folderId,
  tickers,
  onSave,
  onCancel,
  isPending,
}: {
  folderId: string;
  tickers: string[];
  onSave: (data: GuidanceCreate) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const [ticker, setTicker] = useState(tickers[0] || '');
  const [period, setPeriod] = useState('');
  const [metric, setMetric] = useState<MetricType | 'OTHER'>('REVENUE');
  const [guidancePeriod, setGuidancePeriod] = useState('');
  const [guidanceLow, setGuidanceLow] = useState('');
  const [guidanceHigh, setGuidanceHigh] = useState('');
  const [guidancePoint, setGuidancePoint] = useState('');
  const [actualResult, setActualResult] = useState('');
  const [notes, setNotes] = useState('');

  const handleSave = () => {
    const data: GuidanceCreate = {
      folder_id: folderId,
      ticker,
      period,
      metric,
      guidance_period: guidancePeriod,
    };

    // Convert values to raw numbers (millions for non-EPS metrics)
    const isEPS = metric === 'EPS';
    const multiplier = isEPS ? 1 : 1e6;

    if (guidanceLow) data.guidance_low = parseFloat(guidanceLow) * multiplier;
    if (guidanceHigh) data.guidance_high = parseFloat(guidanceHigh) * multiplier;
    if (guidancePoint) data.guidance_point = parseFloat(guidancePoint) * multiplier;
    if (actualResult) data.actual_result = parseFloat(actualResult) * multiplier;
    if (notes) data.notes = notes;

    onSave(data);
  };

  const isEPS = metric === 'EPS';

  return (
    <tr className="bg-primary-50">
      <td className="px-4 py-2">
        <input
          type="text"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          placeholder="2025-Q1"
          className="input w-24"
        />
      </td>
      <td className="px-4 py-2">
        <select value={metric} onChange={(e) => setMetric(e.target.value as MetricType | 'OTHER')} className="input">
          {METRIC_OPTIONS.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      </td>
      <td className="px-4 py-2">
        <input
          type="text"
          value={guidancePeriod}
          onChange={(e) => setGuidancePeriod(e.target.value)}
          placeholder="2024-Q4"
          className="input w-24"
        />
      </td>
      <td className="px-4 py-2">
        <div className="flex gap-1">
          <input
            type="number"
            step="0.01"
            value={guidanceLow}
            onChange={(e) => setGuidanceLow(e.target.value)}
            placeholder={isEPS ? 'Low' : 'Low B'}
            className="input w-20 text-right"
          />
          <span className="self-center text-gray-400">-</span>
          <input
            type="number"
            step="0.01"
            value={guidanceHigh}
            onChange={(e) => setGuidanceHigh(e.target.value)}
            placeholder={isEPS ? 'High' : 'High B'}
            className="input w-20 text-right"
          />
        </div>
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={actualResult}
          onChange={(e) => setActualResult(e.target.value)}
          placeholder={isEPS ? '' : 'B'}
          className="input w-20 text-right"
        />
      </td>
      <td className="px-4 py-2">
        <input type="text" value={notes} onChange={(e) => setNotes(e.target.value)} className="input" />
      </td>
      <td className="px-4 py-2 text-right">
        <button
          onClick={handleSave}
          disabled={isPending || !period || !guidancePeriod}
          className="mr-2 text-green-600 hover:text-green-700"
        >
          <Check className="h-4 w-4" />
        </button>
        <button onClick={onCancel} className="text-gray-400 hover:text-gray-600">
          <X className="h-4 w-4" />
        </button>
      </td>
    </tr>
  );
}

function EditGuidanceRow({
  guidance,
  onSave,
  onCancel,
  isPending,
}: {
  guidance: Guidance;
  onSave: (data: Partial<GuidanceCreate>) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const isEPS = guidance.metric === 'EPS';
  const divisor = isEPS ? 1 : 1e6;

  const [guidanceLow, setGuidanceLow] = useState(
    guidance.guidance_low !== null ? (Number(guidance.guidance_low) / divisor).toFixed(2) : ''
  );
  const [guidanceHigh, setGuidanceHigh] = useState(
    guidance.guidance_high !== null ? (Number(guidance.guidance_high) / divisor).toFixed(2) : ''
  );
  const [guidancePoint, setGuidancePoint] = useState(
    guidance.guidance_point !== null ? (Number(guidance.guidance_point) / divisor).toFixed(2) : ''
  );
  const [actualResult, setActualResult] = useState(
    guidance.actual_result !== null ? (Number(guidance.actual_result) / divisor).toFixed(2) : ''
  );
  const [notes, setNotes] = useState(guidance.notes || '');

  const handleSave = () => {
    const data: Partial<GuidanceCreate> = {};
    const multiplier = isEPS ? 1 : 1e6;

    if (guidanceLow) data.guidance_low = parseFloat(guidanceLow) * multiplier;
    if (guidanceHigh) data.guidance_high = parseFloat(guidanceHigh) * multiplier;
    if (guidancePoint) data.guidance_point = parseFloat(guidancePoint) * multiplier;
    if (actualResult) data.actual_result = parseFloat(actualResult) * multiplier;
    data.notes = notes || undefined;

    onSave(data);
  };

  return (
    <tr className="bg-primary-50">
      <td className="px-4 py-2 text-sm font-medium text-gray-900">{guidance.period}</td>
      <td className="px-4 py-2 text-sm text-gray-500">{guidance.metric}</td>
      <td className="px-4 py-2 text-sm text-gray-500">{guidance.guidance_period}</td>
      <td className="px-4 py-2">
        <div className="flex gap-1">
          <input
            type="number"
            step="0.01"
            value={guidanceLow}
            onChange={(e) => setGuidanceLow(e.target.value)}
            className="input w-20 text-right"
          />
          <span className="self-center text-gray-400">-</span>
          <input
            type="number"
            step="0.01"
            value={guidanceHigh}
            onChange={(e) => setGuidanceHigh(e.target.value)}
            className="input w-20 text-right"
          />
        </div>
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={actualResult}
          onChange={(e) => setActualResult(e.target.value)}
          className="input w-20 text-right"
        />
      </td>
      <td className="px-4 py-2">
        <input type="text" value={notes} onChange={(e) => setNotes(e.target.value)} className="input" />
      </td>
      <td className="px-4 py-2 text-right">
        <button
          onClick={handleSave}
          disabled={isPending}
          className="mr-2 text-green-600 hover:text-green-700"
        >
          <Check className="h-4 w-4" />
        </button>
        <button onClick={onCancel} className="text-gray-400 hover:text-gray-600">
          <X className="h-4 w-4" />
        </button>
      </td>
    </tr>
  );
}

function formatMetricValue(value: number, metric: MetricType | 'OTHER'): string {
  const numValue = Number(value);
  if (metric === 'EPS') {
    return `$${numValue.toFixed(2)}`;
  } else if (metric === 'OTHER') {
    return numValue.toFixed(2);
  } else {
    // Revenue, EBITDA, FCF - show in millions
    return `$${(numValue / 1e6).toFixed(1)}M`;
  }
}
