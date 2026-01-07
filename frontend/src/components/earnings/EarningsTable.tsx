import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2, Check, X, Download } from 'lucide-react';
import { earningsApi } from '../../api/earnings';
import { useToast } from '../ui/Toast';
import type { Earnings, EarningsCreate, MetricType, PeriodType } from '../../types';

interface EarningsTableProps {
  folderId: string;
  tickers: string[];
  earnings: Earnings[];
}

const METRICS: { value: MetricType; label: string }[] = [
  { value: 'EPS', label: 'EPS' },
  { value: 'REVENUE', label: 'Revenue' },
  { value: 'EBITDA', label: 'EBITDA' },
  { value: 'FCF', label: 'Free Cash Flow' },
];

const PERIOD_TYPES: { value: PeriodType; label: string }[] = [
  { value: 'QUARTERLY', label: 'Quarterly' },
  { value: 'ANNUAL', label: 'Annual' },
];

export function EarningsTable({ folderId, tickers, earnings }: EarningsTableProps) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('EPS');
  const [selectedPeriodType, setSelectedPeriodType] = useState<PeriodType>('QUARTERLY');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [isFetching, setIsFetching] = useState(false);

  // Filter earnings by period type
  const filteredEarnings = earnings.filter(e => e.period_type === selectedPeriodType);

  const createMutation = useMutation({
    mutationFn: earningsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['earnings', folderId] });
      addToast('success', 'Earnings added');
      setShowAddForm(false);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string | object | Array<{ msg: string; loc: string[] }> } } };
      const detail = error.response?.data?.detail;

      // Handle Pydantic validation errors (array format)
      if (Array.isArray(detail)) {
        const messages = detail.map((err) => `${err.loc.join('.')}: ${err.msg}`).join(', ');
        addToast('error', messages);
        console.error('Validation errors:', detail);
      } else {
        const message = typeof detail === 'string' ? detail : 'Failed to add earnings';
        addToast('error', message);
        console.error('Error details:', detail);
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<EarningsCreate> }) =>
      earningsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['earnings', folderId] });
      addToast('success', 'Earnings updated');
      setEditingId(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: earningsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['earnings', folderId] });
      addToast('success', 'Earnings deleted');
    },
  });

  const handleFetchFromYahoo = async () => {
    if (tickers.length === 0) {
      addToast('error', 'No tickers available');
      return;
    }

    setIsFetching(true);
    try {
      for (const ticker of tickers) {
        await earningsApi.fetch(folderId, ticker);
      }
      queryClient.invalidateQueries({ queryKey: ['earnings', folderId] });
      addToast('success', `Fetched earnings data for ${tickers.join(', ')}`);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      addToast('error', error.response?.data?.detail || 'Failed to fetch from Yahoo Finance');
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Metric Selector */}
          <div className="flex gap-2">
            {METRICS.map((metric) => (
              <button
                key={metric.value}
                onClick={() => setSelectedMetric(metric.value)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  selectedMetric === metric.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {metric.label}
              </button>
            ))}
          </div>

          {/* Period Type Selector */}
          <select
            value={selectedPeriodType}
            onChange={(e) => setSelectedPeriodType(e.target.value as PeriodType)}
            className="input"
          >
            {PERIOD_TYPES.map((period) => (
              <option key={period.value} value={period.value}>
                {period.label}
              </option>
            ))}
          </select>
        </div>

        {/* Fetch Button */}
        <button
          onClick={handleFetchFromYahoo}
          disabled={isFetching}
          className="btn-secondary"
        >
          <Download className="mr-2 h-4 w-4" />
          {isFetching ? 'Fetching...' : 'Fetch from Yahoo'}
        </button>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Period
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                  Consensus
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                  My Estimate
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">
                  Actual
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
                <AddEarningsRow
                  folderId={folderId}
                  tickers={tickers}
                  metric={selectedMetric}
                  periodType={selectedPeriodType}
                  onSave={(data) => createMutation.mutate(data)}
                  onCancel={() => setShowAddForm(false)}
                  isPending={createMutation.isPending}
                />
              )}
              {filteredEarnings.map((e) =>
                editingId === e.id ? (
                  <EditEarningsRow
                    key={e.id}
                    earnings={e}
                    metric={selectedMetric}
                    onSave={(data) => updateMutation.mutate({ id: e.id, data })}
                    onCancel={() => setEditingId(null)}
                    isPending={updateMutation.isPending}
                  />
                ) : (
                  <EarningsRow
                    key={e.id}
                    earnings={e}
                    metric={selectedMetric}
                    onEdit={() => setEditingId(e.id)}
                    onDelete={() => {
                      if (confirm('Delete this earnings record?')) {
                        deleteMutation.mutate(e.id);
                      }
                    }}
                  />
                )
              )}
              {filteredEarnings.length === 0 && !showAddForm && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-500">
                    No {selectedPeriodType.toLowerCase()} earnings data yet
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
            Add Earnings
          </button>
        </div>
      </div>
    </div>
  );
}

function EarningsRow({
  earnings,
  metric,
  onEdit,
  onDelete,
}: {
  earnings: Earnings;
  metric: MetricType;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const { consensus, myEstimate, actual, surprise } = getMetricValues(earnings, metric);

  return (
    <tr>
      <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
        {earnings.period || earnings.fiscal_quarter}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-500">
        {formatValue(consensus, metric)}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-700">
        {formatValue(myEstimate, metric)}
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-900">
        {formatValue(actual, metric)}
        {surprise !== null && surprise !== undefined && typeof surprise === 'number' && (
          <span
            className={`ml-1 text-xs ${
              surprise >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            ({surprise >= 0 ? '+' : ''}
            {surprise.toFixed(1)}%)
          </span>
        )}
      </td>
      <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-500">
        {earnings.notes || '-'}
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

function AddEarningsRow({
  folderId,
  tickers,
  metric,
  periodType,
  onSave,
  onCancel,
  isPending,
}: {
  folderId: string;
  tickers: string[];
  metric: MetricType;
  periodType: PeriodType;
  onSave: (data: EarningsCreate) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const { addToast } = useToast();
  const [ticker, setTicker] = useState((tickers && tickers[0]) || '');
  const [period, setPeriod] = useState('');
  const [consensus, setConsensus] = useState('');
  const [myEstimate, setMyEstimate] = useState('');
  const [actual, setActual] = useState('');
  const [notes, setNotes] = useState('');

  const handleSave = () => {
    // Validation: period is required
    if (!period || period.trim() === '') {
      addToast('error', 'Period is required (e.g., 2024-Q4 or 2024)');
      return;
    }

    // Validation: ticker is required
    if (!ticker || ticker.trim() === '') {
      addToast('error', 'No ticker available. Please ensure the folder has a ticker assigned.');
      console.error('Tickers array:', tickers);
      return;
    }

    const data: EarningsCreate = {
      folder_id: folderId,
      ticker,
      period_type: periodType,
      period,
      fiscal_quarter: period,
    };

    // Set values based on metric
    const consensusValue = consensus ? parseFloat(consensus) : undefined;
    const myEstimateValue = myEstimate ? parseFloat(myEstimate) : undefined;
    const actualValue = actual ? parseFloat(actual) : undefined;

    if (metric === 'EPS') {
      data.estimate_eps = consensusValue;
      data.my_estimate_eps = myEstimateValue;
      data.actual_eps = actualValue;
    } else if (metric === 'REVENUE') {
      data.estimate_rev = consensusValue ? consensusValue * 1e6 : undefined;
      data.my_estimate_rev = myEstimateValue ? myEstimateValue * 1e6 : undefined;
      data.actual_rev = actualValue ? actualValue * 1e6 : undefined;
    } else if (metric === 'EBITDA') {
      data.estimate_ebitda = consensusValue ? consensusValue * 1e6 : undefined;
      data.my_estimate_ebitda = myEstimateValue ? myEstimateValue * 1e6 : undefined;
      data.actual_ebitda = actualValue ? actualValue * 1e6 : undefined;
    } else if (metric === 'FCF') {
      data.estimate_fcf = consensusValue ? consensusValue * 1e6 : undefined;
      data.my_estimate_fcf = myEstimateValue ? myEstimateValue * 1e6 : undefined;
      data.actual_fcf = actualValue ? actualValue * 1e6 : undefined;
    }

    data.notes = notes || undefined;

    console.log('Submitting earnings data:', data);
    onSave(data);
  };

  return (
    <tr className="bg-primary-50">
      <td className="px-4 py-2">
        <input
          type="text"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          placeholder={periodType === 'QUARTERLY' ? '2024-Q4' : '2024'}
          className="input w-24"
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={consensus}
          onChange={(e) => setConsensus(e.target.value)}
          className="input w-24 text-right"
          placeholder={metric !== 'EPS' ? 'M' : ''}
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={myEstimate}
          onChange={(e) => setMyEstimate(e.target.value)}
          className="input w-24 text-right"
          placeholder={metric !== 'EPS' ? 'M' : ''}
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={actual}
          onChange={(e) => setActual(e.target.value)}
          className="input w-24 text-right"
          placeholder={metric !== 'EPS' ? 'M' : ''}
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="input"
        />
      </td>
      <td className="px-4 py-2 text-right">
        <button
          onClick={handleSave}
          disabled={isPending || !period}
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

function EditEarningsRow({
  earnings,
  metric,
  onSave,
  onCancel,
  isPending,
}: {
  earnings: Earnings;
  metric: MetricType;
  onSave: (data: Partial<EarningsCreate>) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const { consensus, myEstimate, actual } = getMetricValues(earnings, metric);

  const [consensusValue, setConsensusValue] = useState(
    consensus !== null ? (metric === 'EPS' ? consensus.toString() : (consensus / 1e6).toFixed(2)) : ''
  );
  const [myEstimateValue, setMyEstimateValue] = useState(
    myEstimate !== null ? (metric === 'EPS' ? myEstimate.toString() : (myEstimate / 1e6).toFixed(2)) : ''
  );
  const [actualValue, setActualValue] = useState(
    actual !== null ? (metric === 'EPS' ? actual.toString() : (actual / 1e6).toFixed(2)) : ''
  );
  const [notes, setNotes] = useState(earnings.notes || '');

  const handleSave = () => {
    const data: Partial<EarningsCreate> = {};

    const consensusNum = consensusValue ? parseFloat(consensusValue) : undefined;
    const myEstimateNum = myEstimateValue ? parseFloat(myEstimateValue) : undefined;
    const actualNum = actualValue ? parseFloat(actualValue) : undefined;

    if (metric === 'EPS') {
      data.estimate_eps = consensusNum;
      data.my_estimate_eps = myEstimateNum;
      data.actual_eps = actualNum;
    } else if (metric === 'REVENUE') {
      data.estimate_rev = consensusNum ? consensusNum * 1e6 : undefined;
      data.my_estimate_rev = myEstimateNum ? myEstimateNum * 1e6 : undefined;
      data.actual_rev = actualNum ? actualNum * 1e6 : undefined;
    } else if (metric === 'EBITDA') {
      data.estimate_ebitda = consensusNum ? consensusNum * 1e6 : undefined;
      data.my_estimate_ebitda = myEstimateNum ? myEstimateNum * 1e6 : undefined;
      data.actual_ebitda = actualNum ? actualNum * 1e6 : undefined;
    } else if (metric === 'FCF') {
      data.estimate_fcf = consensusNum ? consensusNum * 1e6 : undefined;
      data.my_estimate_fcf = myEstimateNum ? myEstimateNum * 1e6 : undefined;
      data.actual_fcf = actualNum ? actualNum * 1e6 : undefined;
    }

    data.notes = notes || undefined;
    onSave(data);
  };

  return (
    <tr className="bg-primary-50">
      <td className="px-4 py-2 text-sm font-medium text-gray-900">
        {earnings.period || earnings.fiscal_quarter}
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={consensusValue}
          onChange={(e) => setConsensusValue(e.target.value)}
          className="input w-24 text-right"
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={myEstimateValue}
          onChange={(e) => setMyEstimateValue(e.target.value)}
          className="input w-24 text-right"
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          value={actualValue}
          onChange={(e) => setActualValue(e.target.value)}
          className="input w-24 text-right"
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="input"
        />
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

function getMetricValues(earnings: Earnings, metric: MetricType) {
  if (metric === 'EPS') {
    return {
      consensus: earnings.estimate_eps,
      myEstimate: earnings.my_estimate_eps,
      actual: earnings.actual_eps,
      surprise: earnings.eps_surprise_pct,
    };
  } else if (metric === 'REVENUE') {
    return {
      consensus: earnings.estimate_rev,
      myEstimate: earnings.my_estimate_rev,
      actual: earnings.actual_rev,
      surprise: earnings.rev_surprise_pct,
    };
  } else if (metric === 'EBITDA') {
    return {
      consensus: earnings.estimate_ebitda,
      myEstimate: earnings.my_estimate_ebitda,
      actual: earnings.actual_ebitda,
      surprise: earnings.ebitda_surprise_pct,
    };
  } else {
    // FCF
    return {
      consensus: earnings.estimate_fcf,
      myEstimate: earnings.my_estimate_fcf,
      actual: earnings.actual_fcf,
      surprise: earnings.fcf_surprise_pct,
    };
  }
}

function formatValue(value: number | null | undefined, metric: MetricType): string {
  if (value === null || value === undefined) return '-';

  if (metric === 'EPS') {
    return `$${Number(value).toFixed(2)}`;
  } else {
    // Revenue, EBITDA, FCF - show in millions
    return `$${(Number(value) / 1e6).toFixed(1)}M`;
  }
}
