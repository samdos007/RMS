import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  RefreshCw,
  Download,
  Plus,
  Pencil,
  Trash2,
} from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
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
import { ideasApi } from '../api/ideas';
import { notesApi } from '../api/notes';
import { pricesApi } from '../api/prices';
import { attachmentsApi } from '../api/attachments';
import { PageLoader, LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Modal } from '../components/ui/Modal';
import { useToast } from '../components/ui/Toast';
import { PnLDisplay } from '../components/ideas/PnLDisplay';
import { StatusBadge } from '../components/ideas/StatusBadge';
import type { Idea, Note, NoteType, IdeaStatus } from '../types';

export function IdeaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [isCloseModalOpen, setIsCloseModalOpen] = useState(false);
  const [isNoteModalOpen, setIsNoteModalOpen] = useState(false);

  const { data: idea, isLoading } = useQuery({
    queryKey: ['idea', id],
    queryFn: () => ideasApi.get(id!),
    enabled: !!id,
  });

  const { data: pnlHistory } = useQuery({
    queryKey: ['idea-pnl-history', id],
    queryFn: () => ideasApi.getPnlHistory(id!),
    enabled: !!id,
  });

  const { data: notes } = useQuery({
    queryKey: ['idea-notes', id],
    queryFn: () => notesApi.listForIdea(id!),
    enabled: !!id,
  });

  const { data: attachments } = useQuery({
    queryKey: ['idea-attachments', id],
    queryFn: () => attachmentsApi.listForIdea(id!),
    enabled: !!id,
  });

  const fetchPricesMutation = useMutation({
    mutationFn: () => pricesApi.fetchLatest(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idea', id] });
      queryClient.invalidateQueries({ queryKey: ['idea-pnl-history', id] });
      addToast('success', 'Prices updated');
    },
    onError: () => {
      addToast('error', 'Failed to fetch prices');
    },
  });

  const backfillMutation = useMutation({
    mutationFn: () => pricesApi.backfill(id!),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['idea-pnl-history', id] });
      addToast('success', `Created ${result.snapshots_created} price snapshots`);
    },
    onError: () => {
      addToast('error', 'Failed to backfill prices');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => ideasApi.delete(id!),
    onSuccess: () => {
      addToast('success', 'Idea deleted');
      navigate(`/folders/${idea?.folder_id}`);
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: IdeaStatus) => ideasApi.updateStatus(id!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idea', id] });
      addToast('success', 'Status updated');
    },
  });

  if (isLoading) {
    return <PageLoader />;
  }

  if (!idea) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Idea not found</p>
      </div>
    );
  }

  const isPair = idea.trade_type === 'PAIR_LONG_SHORT';
  const isClosed = idea.status === 'CLOSED' || idea.status === 'KILLED';

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link
          to={`/folders/${idea.folder_id}`}
          className="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back to {idea.folder_name}
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{idea.title}</h1>
              <StatusBadge status={idea.status} />
            </div>
            <p className="mt-1 text-sm text-gray-500">
              {idea.trade_type === 'PAIR_LONG_SHORT' ? 'Pair Trade' : idea.trade_type}
              {' · '}Started {format(new Date(idea.start_date), 'MMM d, yyyy')}
              {idea.horizon !== 'OTHER' && ` · ${idea.horizon.replace('_', '-')}`}
            </p>
          </div>

          <div className="flex items-center gap-4">
            <PnLDisplay
              pnlPercent={idea.pnl_percent}
              pnlAbsolute={idea.pnl_absolute}
              isRealized={isClosed}
              size="lg"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <button
          onClick={() => fetchPricesMutation.mutate()}
          disabled={fetchPricesMutation.isPending}
          className="btn-secondary"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${fetchPricesMutation.isPending ? 'animate-spin' : ''}`} />
          Fetch Prices
        </button>

        <button
          onClick={() => backfillMutation.mutate()}
          disabled={backfillMutation.isPending}
          className="btn-secondary"
        >
          <Download className="mr-2 h-4 w-4" />
          Backfill History
        </button>

        {!isClosed && (
          <>
            <select
              value={idea.status}
              onChange={(e) => {
                const newStatus = e.target.value as IdeaStatus;
                if (newStatus === 'CLOSED' || newStatus === 'KILLED') {
                  setIsCloseModalOpen(true);
                } else {
                  updateStatusMutation.mutate(newStatus);
                }
              }}
              className="input w-auto"
            >
              <option value="DRAFT">Draft</option>
              <option value="ACTIVE">Active</option>
              <option value="SCALED_UP">Scaled Up</option>
              <option value="TRIMMED">Trimmed</option>
              <option value="CLOSED">Close Position</option>
              <option value="KILLED">Kill Position</option>
            </select>
          </>
        )}

        <Link to={`/ideas/${id}/edit`} className="btn-secondary">
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </Link>

        <button
          onClick={() => {
            if (confirm('Delete this idea?')) {
              deleteMutation.mutate();
            }
          }}
          className="btn-danger"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Position Details */}
          <div className="card p-6">
            <h2 className="mb-4 text-lg font-medium text-gray-900">Position Details</h2>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">Entry Price</dt>
                <dd className="font-medium">${Number(idea.entry_price_primary).toFixed(2)}</dd>
              </div>
              {idea.current_price_primary && (
                <div>
                  <dt className="text-gray-500">Current Price</dt>
                  <dd className="font-medium">${Number(idea.current_price_primary).toFixed(2)}</dd>
                </div>
              )}
              {isPair && (
                <>
                  <div>
                    <dt className="text-gray-500">Secondary Entry</dt>
                    <dd className="font-medium">${Number(idea.entry_price_secondary).toFixed(2)}</dd>
                  </div>
                  {idea.current_price_secondary && (
                    <div>
                      <dt className="text-gray-500">Secondary Current</dt>
                      <dd className="font-medium">${Number(idea.current_price_secondary).toFixed(2)}</dd>
                    </div>
                  )}
                </>
              )}
              {Number(idea.position_size) > 0 && (
                <div>
                  <dt className="text-gray-500">Position Size</dt>
                  <dd className="font-medium">{idea.position_size}</dd>
                </div>
              )}
              {idea.target_price_primary && (
                <div>
                  <dt className="text-gray-500">Target</dt>
                  <dd className="font-medium text-green-600">
                    ${Number(idea.target_price_primary).toFixed(2)}
                  </dd>
                </div>
              )}
              {idea.stop_level_primary && (
                <div>
                  <dt className="text-gray-500">Stop</dt>
                  <dd className="font-medium text-red-600">
                    ${Number(idea.stop_level_primary).toFixed(2)}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          {/* P&L Chart */}
          {pnlHistory && pnlHistory.history.length > 0 && (
            <div className="card p-6">
              <h2 className="mb-4 text-lg font-medium text-gray-900">P&L History</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={pnlHistory.history.map((h) => ({
                    ...h,
                    pnl_percent: Number(h.pnl_percent) * 100,
                    pnl_primary_leg: h.pnl_primary_leg ? Number(h.pnl_primary_leg) * 100 : null,
                    pnl_secondary_leg: h.pnl_secondary_leg ? Number(h.pnl_secondary_leg) * 100 : null,
                    date: format(new Date(h.timestamp), 'MM/dd'),
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    tickFormatter={(v) => `${v.toFixed(1)}%`}
                  />
                  <Tooltip formatter={(v: number) => `${v.toFixed(2)}%`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="pnl_percent"
                    name="Spread P&L"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    dot={false}
                  />
                  {isPair && (
                    <>
                      <Line
                        type="monotone"
                        dataKey="pnl_primary_leg"
                        name="Long Leg"
                        stroke="#10b981"
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="pnl_secondary_leg"
                        name="Short Leg"
                        stroke="#ef4444"
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </>
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Thesis */}
          {idea.thesis_md && (
            <div className="card p-6">
              <h2 className="mb-4 text-lg font-medium text-gray-900">Thesis</h2>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{idea.thesis_md}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Catalysts & Risks */}
          <div className="grid grid-cols-2 gap-6">
            {idea.catalysts.length > 0 && (
              <div className="card p-6">
                <h2 className="mb-4 text-lg font-medium text-gray-900">Catalysts</h2>
                <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
                  {idea.catalysts.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </div>
            )}

            {idea.risks.length > 0 && (
              <div className="card p-6">
                <h2 className="mb-4 text-lg font-medium text-gray-900">Risks</h2>
                <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
                  {idea.risks.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Kill Criteria */}
          {idea.kill_criteria_md && (
            <div className="card p-6">
              <h2 className="mb-4 text-lg font-medium text-gray-900">Kill Criteria</h2>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{idea.kill_criteria_md}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Notes */}
          <div className="card p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Notes</h2>
              <button
                onClick={() => setIsNoteModalOpen(true)}
                className="btn-secondary text-xs"
              >
                <Plus className="mr-1 h-3 w-3" />
                Add
              </button>
            </div>

            {notes && notes.length > 0 ? (
              <div className="space-y-4">
                {notes.map((note) => (
                  <NoteCard key={note.id} note={note} ideaId={id!} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No notes yet</p>
            )}
          </div>

          {/* Attachments */}
          <div className="card p-6">
            <h2 className="mb-4 text-lg font-medium text-gray-900">Attachments</h2>

            {attachments && attachments.length > 0 ? (
              <div className="space-y-2">
                {attachments.map((a) => (
                  <a
                    key={a.id}
                    href={attachmentsApi.download(a.id)}
                    className="block rounded border p-2 text-sm hover:bg-gray-50"
                  >
                    {a.filename}
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No attachments</p>
            )}
          </div>
        </div>
      </div>

      {/* Close Modal */}
      <CloseIdeaModal
        isOpen={isCloseModalOpen}
        onClose={() => setIsCloseModalOpen(false)}
        idea={idea}
      />

      {/* Add Note Modal */}
      <AddNoteModal
        isOpen={isNoteModalOpen}
        onClose={() => setIsNoteModalOpen(false)}
        ideaId={id!}
      />
    </div>
  );
}

function NoteCard({ note, ideaId }: { note: Note; ideaId: string }) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const deleteMutation = useMutation({
    mutationFn: () => notesApi.delete(note.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idea-notes', ideaId] });
      addToast('success', 'Note deleted');
    },
  });

  return (
    <div className="border-l-2 border-gray-200 pl-3">
      <div className="flex items-center justify-between">
        <span className="badge-gray text-xs">{note.note_type}</span>
        <button
          onClick={() => deleteMutation.mutate()}
          className="text-gray-400 hover:text-red-500"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
      <div className="mt-1 text-sm text-gray-600">
        <ReactMarkdown>{note.content_md}</ReactMarkdown>
      </div>
      <p className="mt-1 text-xs text-gray-400">
        {format(new Date(note.created_at), 'MMM d, yyyy')}
      </p>
    </div>
  );
}

function CloseIdeaModal({
  isOpen,
  onClose,
  idea,
}: {
  isOpen: boolean;
  onClose: () => void;
  idea: Idea;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [status, setStatus] = useState<'CLOSED' | 'KILLED'>('CLOSED');
  const [exitPricePrimary, setExitPricePrimary] = useState('');
  const [exitPriceSecondary, setExitPriceSecondary] = useState('');
  const [exitDate, setExitDate] = useState(new Date().toISOString().split('T')[0]);
  const [postmortem, setPostmortem] = useState('');

  const closeMutation = useMutation({
    mutationFn: () =>
      ideasApi.close(idea.id, {
        status,
        exit_price_primary: parseFloat(exitPricePrimary),
        exit_price_secondary: idea.trade_type === 'PAIR_LONG_SHORT'
          ? parseFloat(exitPriceSecondary)
          : undefined,
        exit_date: exitDate,
        postmortem_note: postmortem || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idea', idea.id] });
      addToast('success', 'Position closed');
      onClose();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      addToast('error', error.response?.data?.detail || 'Failed to close position');
    },
  });

  const isPair = idea.trade_type === 'PAIR_LONG_SHORT';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Close Position">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          closeMutation.mutate();
        }}
        className="space-y-4"
      >
        <div>
          <label className="label mb-1">Close Type</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="CLOSED"
                checked={status === 'CLOSED'}
                onChange={() => setStatus('CLOSED')}
                className="mr-2"
              />
              Close (Realized P&L)
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="KILLED"
                checked={status === 'KILLED'}
                onChange={() => setStatus('KILLED')}
                className="mr-2"
              />
              Kill (Stop Out)
            </label>
          </div>
        </div>

        <div>
          <label className="label mb-1">Exit Price (Primary) *</label>
          <input
            type="number"
            step="0.01"
            value={exitPricePrimary}
            onChange={(e) => setExitPricePrimary(e.target.value)}
            className="input"
            required
          />
        </div>

        {isPair && (
          <div>
            <label className="label mb-1">Exit Price (Secondary) *</label>
            <input
              type="number"
              step="0.01"
              value={exitPriceSecondary}
              onChange={(e) => setExitPriceSecondary(e.target.value)}
              className="input"
              required
            />
          </div>
        )}

        <div>
          <label className="label mb-1">Exit Date *</label>
          <input
            type="date"
            value={exitDate}
            onChange={(e) => setExitDate(e.target.value)}
            className="input"
            required
          />
        </div>

        <div>
          <label className="label mb-1">Post-Mortem Note</label>
          <textarea
            value={postmortem}
            onChange={(e) => setPostmortem(e.target.value)}
            rows={4}
            className="input"
            placeholder="What did you learn? What would you do differently?"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={closeMutation.isPending}
            className="btn-primary"
          >
            {closeMutation.isPending ? 'Closing...' : 'Close Position'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AddNoteModal({
  isOpen,
  onClose,
  ideaId,
}: {
  isOpen: boolean;
  onClose: () => void;
  ideaId: string;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [noteType, setNoteType] = useState<NoteType>('GENERAL');
  const [content, setContent] = useState('');

  const createMutation = useMutation({
    mutationFn: () =>
      notesApi.create({
        idea_id: ideaId,
        note_type: noteType,
        content_md: content,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idea-notes', ideaId] });
      addToast('success', 'Note added');
      onClose();
      setContent('');
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Note">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          createMutation.mutate();
        }}
        className="space-y-4"
      >
        <div>
          <label className="label mb-1">Type</label>
          <select
            value={noteType}
            onChange={(e) => setNoteType(e.target.value as NoteType)}
            className="input"
          >
            <option value="GENERAL">General</option>
            <option value="EARNINGS">Earnings</option>
            <option value="CHANNEL_CHECK">Channel Check</option>
            <option value="VALUATION">Valuation</option>
            <option value="RISK">Risk</option>
          </select>
        </div>

        <div>
          <label className="label mb-1">Content (Markdown)</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="input font-mono text-sm"
            required
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="btn-primary"
          >
            {createMutation.isPending ? 'Adding...' : 'Add Note'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
