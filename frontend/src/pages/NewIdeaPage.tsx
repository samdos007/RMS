import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft } from 'lucide-react';
import { foldersApi } from '../api/folders';
import { ideasApi } from '../api/ideas';
import { useToast } from '../components/ui/Toast';
import { PageLoader } from '../components/ui/LoadingSpinner';
import type { IdeaCreate, TradeType, PairOrientation, Horizon } from '../types';

export function NewIdeaPage() {
  const { id: folderId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const { data: folder, isLoading } = useQuery({
    queryKey: ['folder', folderId],
    queryFn: () => foldersApi.get(folderId!),
    enabled: !!folderId,
  });

  const createMutation = useMutation({
    mutationFn: ideasApi.create,
    onSuccess: (idea) => {
      addToast('success', 'Idea created');
      navigate(`/ideas/${idea.id}`);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      addToast('error', error.response?.data?.detail || 'Failed to create idea');
    },
  });

  const [formData, setFormData] = useState<{
    title: string;
    trade_type: TradeType;
    pair_orientation: PairOrientation;
    start_date: string;
    entry_price_primary: string;
    entry_price_secondary: string;
    position_size: string;
    horizon: Horizon;
    thesis_md: string;
    catalysts: string;
    risks: string;
    kill_criteria_md: string;
    target_price_primary: string;
    stop_level_primary: string;
    target_price_secondary: string;
    stop_level_secondary: string;
  }>({
    title: '',
    trade_type: 'LONG',
    pair_orientation: 'LONG_PRIMARY_SHORT_SECONDARY',
    start_date: new Date().toISOString().split('T')[0],
    entry_price_primary: '',
    entry_price_secondary: '',
    position_size: '',
    horizon: 'OTHER',
    thesis_md: '',
    catalysts: '',
    risks: '',
    kill_criteria_md: '',
    target_price_primary: '',
    stop_level_primary: '',
    target_price_secondary: '',
    stop_level_secondary: '',
  });

  if (isLoading) {
    return <PageLoader />;
  }

  if (!folder) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Folder not found</p>
      </div>
    );
  }

  const isPair = folder.type === 'PAIR';
  const showPairFields = formData.trade_type === 'PAIR_LONG_SHORT' && isPair;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const data: IdeaCreate = {
      folder_id: folderId!,
      title: formData.title,
      trade_type: formData.trade_type,
      pair_orientation: showPairFields ? formData.pair_orientation : undefined,
      start_date: formData.start_date,
      entry_price_primary: parseFloat(formData.entry_price_primary),
      entry_price_secondary: showPairFields && formData.entry_price_secondary
        ? parseFloat(formData.entry_price_secondary)
        : undefined,
      position_size: formData.position_size ? parseFloat(formData.position_size) : undefined,
      horizon: formData.horizon,
      thesis_md: formData.thesis_md || undefined,
      catalysts: formData.catalysts
        ? formData.catalysts.split('\n').filter(Boolean)
        : [],
      risks: formData.risks
        ? formData.risks.split('\n').filter(Boolean)
        : [],
      kill_criteria_md: formData.kill_criteria_md || undefined,
      target_price_primary: formData.target_price_primary
        ? parseFloat(formData.target_price_primary)
        : undefined,
      stop_level_primary: formData.stop_level_primary
        ? parseFloat(formData.stop_level_primary)
        : undefined,
      target_price_secondary: showPairFields && formData.target_price_secondary
        ? parseFloat(formData.target_price_secondary)
        : undefined,
      stop_level_secondary: showPairFields && formData.stop_level_secondary
        ? parseFloat(formData.stop_level_secondary)
        : undefined,
    };

    createMutation.mutate(data);
  };

  return (
    <div className="max-w-3xl">
      <Link
        to={`/folders/${folderId}`}
        className="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="mr-1 h-4 w-4" />
        Back to {folder.name}
      </Link>

      <h1 className="mb-6 text-2xl font-bold text-gray-900">New Idea</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="card p-6">
          <h2 className="mb-4 text-lg font-medium text-gray-900">Basic Info</h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="title" className="label mb-1">
                Title *
              </label>
              <input
                id="title"
                type="text"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                className="input"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label mb-1">Trade Type *</label>
                <select
                  value={formData.trade_type}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      trade_type: e.target.value as TradeType,
                    })
                  }
                  className="input"
                >
                  <option value="LONG">Long</option>
                  <option value="SHORT">Short</option>
                  {isPair && (
                    <option value="PAIR_LONG_SHORT">Pair (Long/Short)</option>
                  )}
                </select>
              </div>

              <div>
                <label htmlFor="start_date" className="label mb-1">
                  Start Date *
                </label>
                <input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) =>
                    setFormData({ ...formData, start_date: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>
            </div>

            {showPairFields && (
              <div>
                <label className="label mb-1">Pair Orientation</label>
                <select
                  value={formData.pair_orientation}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      pair_orientation: e.target.value as PairOrientation,
                    })
                  }
                  className="input"
                >
                  <option value="LONG_PRIMARY_SHORT_SECONDARY">
                    Long {folder.ticker_primary} / Short {folder.ticker_secondary}
                  </option>
                  <option value="SHORT_PRIMARY_LONG_SECONDARY">
                    Short {folder.ticker_primary} / Long {folder.ticker_secondary}
                  </option>
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label mb-1">Horizon</label>
                <select
                  value={formData.horizon}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      horizon: e.target.value as Horizon,
                    })
                  }
                  className="input"
                >
                  <option value="EVENT">Event</option>
                  <option value="3_6MO">3-6 Months</option>
                  <option value="6_12MO">6-12 Months</option>
                  <option value="SECULAR">Secular</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="position_size" className="label mb-1">
                  Position Size (% or units)
                </label>
                <input
                  id="position_size"
                  type="number"
                  step="0.01"
                  value={formData.position_size}
                  onChange={(e) =>
                    setFormData({ ...formData, position_size: e.target.value })
                  }
                  className="input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Entry Prices */}
        <div className="card p-6">
          <h2 className="mb-4 text-lg font-medium text-gray-900">Entry Prices</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="entry_price_primary" className="label mb-1">
                {folder.ticker_primary} Entry Price *
              </label>
              <input
                id="entry_price_primary"
                type="number"
                step="0.01"
                value={formData.entry_price_primary}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    entry_price_primary: e.target.value,
                  })
                }
                className="input"
                required
              />
            </div>

            {showPairFields && (
              <div>
                <label htmlFor="entry_price_secondary" className="label mb-1">
                  {folder.ticker_secondary} Entry Price *
                </label>
                <input
                  id="entry_price_secondary"
                  type="number"
                  step="0.01"
                  value={formData.entry_price_secondary}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      entry_price_secondary: e.target.value,
                    })
                  }
                  className="input"
                  required
                />
              </div>
            )}
          </div>
        </div>

        {/* Targets & Stops */}
        <div className="card p-6">
          <h2 className="mb-4 text-lg font-medium text-gray-900">Targets & Stops</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label mb-1">
                {folder.ticker_primary} Target
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.target_price_primary}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    target_price_primary: e.target.value,
                  })
                }
                className="input"
              />
            </div>

            <div>
              <label className="label mb-1">
                {folder.ticker_primary} Stop
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.stop_level_primary}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    stop_level_primary: e.target.value,
                  })
                }
                className="input"
              />
            </div>

            {showPairFields && (
              <>
                <div>
                  <label className="label mb-1">
                    {folder.ticker_secondary} Target
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.target_price_secondary}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        target_price_secondary: e.target.value,
                      })
                    }
                    className="input"
                  />
                </div>

                <div>
                  <label className="label mb-1">
                    {folder.ticker_secondary} Stop
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.stop_level_secondary}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        stop_level_secondary: e.target.value,
                      })
                    }
                    className="input"
                  />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Thesis */}
        <div className="card p-6">
          <h2 className="mb-4 text-lg font-medium text-gray-900">Thesis & Analysis</h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="thesis" className="label mb-1">
                Thesis (Markdown)
              </label>
              <textarea
                id="thesis"
                value={formData.thesis_md}
                onChange={(e) =>
                  setFormData({ ...formData, thesis_md: e.target.value })
                }
                rows={6}
                className="input font-mono text-sm"
                placeholder="Why this trade? What's your edge?"
              />
            </div>

            <div>
              <label htmlFor="catalysts" className="label mb-1">
                Catalysts (one per line)
              </label>
              <textarea
                id="catalysts"
                value={formData.catalysts}
                onChange={(e) =>
                  setFormData({ ...formData, catalysts: e.target.value })
                }
                rows={3}
                className="input"
                placeholder="Earnings beat&#10;Product launch&#10;Analyst upgrade"
              />
            </div>

            <div>
              <label htmlFor="risks" className="label mb-1">
                Risks (one per line)
              </label>
              <textarea
                id="risks"
                value={formData.risks}
                onChange={(e) =>
                  setFormData({ ...formData, risks: e.target.value })
                }
                rows={3}
                className="input"
                placeholder="Competition&#10;Regulatory&#10;Macro"
              />
            </div>

            <div>
              <label htmlFor="kill_criteria" className="label mb-1">
                Kill Criteria (Markdown)
              </label>
              <textarea
                id="kill_criteria"
                value={formData.kill_criteria_md}
                onChange={(e) =>
                  setFormData({ ...formData, kill_criteria_md: e.target.value })
                }
                rows={3}
                className="input font-mono text-sm"
                placeholder="When would you exit regardless of price?"
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <Link to={`/folders/${folderId}`} className="btn-secondary">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="btn-primary"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Idea'}
          </button>
        </div>
      </form>
    </div>
  );
}
