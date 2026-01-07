import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../components/ui/Modal';
import {
  Plus,
  ArrowLeft,
  FileText,
  BarChart3,
  Paperclip,
  RefreshCw,
  Download,
  Upload,
  Trash2
} from 'lucide-react';
import { format } from 'date-fns';
import { foldersApi } from '../api/folders';
import { ideasApi } from '../api/ideas';
import { earningsApi } from '../api/earnings';
import { attachmentsApi } from '../api/attachments';
import { notesApi } from '../api/notes';
import { LoadingSpinner, PageLoader } from '../components/ui/LoadingSpinner';
import { useToast } from '../components/ui/Toast';
import { PnLDisplay } from '../components/ideas/PnLDisplay';
import { StatusBadge } from '../components/ideas/StatusBadge';
import { EarningsTable } from '../components/earnings/EarningsTable';
import { EarningsChart } from '../components/earnings/EarningsChart';
import { GuidanceTable } from '../components/guidance/GuidanceTable';
import { ThemeSelector } from '../components/themes/ThemeSelector';
import { ThemePerformance } from '../components/themes/ThemePerformance';
import type { Idea, Attachment, Note, NoteType } from '../types';

type TabType = 'ideas' | 'earnings' | 'guidance' | 'attachments' | 'performance' | 'notes';

export function FolderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('ideas');

  const { data: folder, isLoading: folderLoading } = useQuery({
    queryKey: ['folder', id],
    queryFn: () => foldersApi.get(id!),
    enabled: !!id,
  });

  const { data: ideasData, isLoading: ideasLoading } = useQuery({
    queryKey: ['ideas', id],
    queryFn: () => ideasApi.list(id, undefined, true),
    enabled: !!id && activeTab === 'ideas',
  });

  const { data: earningsData, isLoading: earningsLoading } = useQuery({
    queryKey: ['earnings', id],
    queryFn: () => earningsApi.list(id!),
    enabled: !!id && activeTab === 'earnings',
  });

  const { data: attachments, isLoading: attachmentsLoading } = useQuery({
    queryKey: ['folder-attachments', id],
    queryFn: () => attachmentsApi.listForFolder(id!),
    enabled: !!id && activeTab === 'attachments',
  });

  if (folderLoading) {
    return <PageLoader />;
  }

  if (!folder) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Folder not found</p>
        <Link to="/folders" className="btn-primary mt-4">
          Back to Folders
        </Link>
      </div>
    );
  }

  // Define tabs based on folder type
  const tabs: { key: TabType; label: string; icon: typeof FileText }[] =
    folder.type === 'THEME'
      ? [
          { key: 'ideas', label: 'Ideas', icon: FileText },
          { key: 'performance', label: 'Performance', icon: BarChart3 },
          { key: 'notes', label: 'Notes', icon: FileText },
          { key: 'attachments', label: 'Attachments', icon: Paperclip },
        ]
      : [
          { key: 'ideas', label: 'Ideas', icon: FileText },
          { key: 'earnings', label: 'Earnings', icon: BarChart3 },
          { key: 'guidance', label: 'Guidance', icon: RefreshCw },
          { key: 'attachments', label: 'Attachments', icon: Paperclip },
        ];

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/folders"
          className="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back to Folders
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{folder.name}</h1>
            <p className="mt-1 text-sm text-gray-500">
              {folder.type === 'PAIR' ? 'Pair Trade' : folder.type === 'THEME' ? 'Theme' : 'Single Ticker'}
              {folder.description && ` - ${folder.description}`}
            </p>
          </div>

          <Link
            to={`/folders/${id}/ideas/new`}
            className="btn-primary"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Idea
          </Link>
        </div>

        {folder.tags.length > 0 && (
          <div className="mt-3 flex gap-2">
            {folder.tags.map((tag) => (
              <span key={tag} className="badge-gray">{tag}</span>
            ))}
          </div>
        )}

        {/* Theme-specific details */}
        {folder.type === 'THEME' && (
          <div className="mt-6 space-y-4">
            <div className="card p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Theme Details</h3>

              {folder.theme_date && (
                <div className="mb-3">
                  <span className="text-sm font-medium text-gray-500">Date: </span>
                  <span className="text-sm text-gray-900">
                    {format(new Date(folder.theme_date), 'MMM d, yyyy')}
                  </span>
                </div>
              )}

              {folder.theme_thesis && (
                <div className="mb-3">
                  <span className="text-sm font-medium text-gray-500 block mb-1">Thesis:</span>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{folder.theme_thesis}</p>
                </div>
              )}

              {folder.theme_tickers.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-500 block mb-2">Tickers:</span>
                  <div className="flex flex-wrap gap-2">
                    {folder.theme_tickers.map((ticker) => (
                      <div
                        key={ticker.ticker}
                        className="flex items-center gap-2 rounded border border-gray-300 bg-gray-50 px-3 py-1"
                      >
                        <span className="font-semibold text-gray-900">{ticker.ticker}</span>
                        {ticker.pnl !== undefined && ticker.pnl !== null && (
                          <span
                            className={`text-sm font-medium ${
                              ticker.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {ticker.pnl >= 0 ? '+' : ''}
                            {ticker.pnl.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ThemeSelector for SINGLE/PAIR folders */}
        {(folder.type === 'SINGLE' || folder.type === 'PAIR') && (
          <div className="mt-6">
            <ThemeSelectorWithMutation folderId={id!} initialThemes={folder.theme_ids} />
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium ${
                  activeTab === tab.key
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'ideas' && (
          <IdeasTab
            ideas={ideasData?.ideas || []}
            isLoading={ideasLoading}
            folderId={id!}
          />
        )}
        {activeTab === 'earnings' && (
          <>
            {console.log('Folder data:', folder)}
            <EarningsTab
              folderId={id!}
              tickers={folder.tickers || []}
              earnings={earningsData?.earnings || []}
              isLoading={earningsLoading}
            />
          </>
        )}
        {activeTab === 'guidance' && (
          <GuidanceTab
            folderId={id!}
            tickers={folder.tickers}
          />
        )}
        {activeTab === 'attachments' && (
          <AttachmentsTab
            folderId={id!}
            attachments={attachments || []}
            isLoading={attachmentsLoading}
          />
        )}
        {activeTab === 'performance' && folder.type === 'THEME' && (
          <PerformanceTab
            folderId={id!}
            themeDate={folder.theme_date!}
          />
        )}
        {activeTab === 'notes' && folder.type === 'THEME' && (
          <NotesTab folderId={id!} />
        )}
      </div>
    </div>
  );
}

function ThemeSelectorWithMutation({
  folderId,
  initialThemes,
}: {
  folderId: string;
  initialThemes: string[];
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const updateThemesMutation = useMutation({
    mutationFn: (themeIds: string[]) => foldersApi.addFolderToThemes(folderId, themeIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folder', folderId] });
      addToast('success', 'Themes updated');
    },
    onError: () => {
      addToast('error', 'Failed to update themes');
    },
  });

  return (
    <ThemeSelector
      selectedThemes={initialThemes}
      onSelectionChange={(themeIds) => updateThemesMutation.mutate(themeIds)}
    />
  );
}

function IdeasTab({
  ideas,
  isLoading,
  folderId,
}: {
  ideas: Idea[];
  isLoading: boolean;
  folderId: string;
}) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (ideas.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
        <FileText className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No ideas yet</h3>
        <p className="mt-2 text-sm text-gray-500">
          Create your first trade idea for this folder.
        </p>
        <Link to={`/folders/${folderId}/ideas/new`} className="btn-primary mt-4">
          <Plus className="mr-2 h-4 w-4" />
          New Idea
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {ideas.map((idea) => (
        <Link
          key={idea.id}
          to={`/ideas/${idea.id}`}
          className="card block p-4 hover:bg-gray-50"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h3 className="font-medium text-gray-900">{idea.title}</h3>
                <StatusBadge status={idea.status} />
                <span className="text-sm text-gray-500">
                  {idea.trade_type === 'PAIR_LONG_SHORT'
                    ? 'Pair'
                    : idea.trade_type}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Started {format(new Date(idea.start_date), 'MMM d, yyyy')}
                {idea.horizon !== 'OTHER' && ` · ${idea.horizon.replace('_', '-')}`}
              </p>
            </div>
            <PnLDisplay
              pnlPercent={idea.pnl_percent}
              pnlAbsolute={idea.pnl_absolute}
              isRealized={idea.status === 'CLOSED' || idea.status === 'KILLED'}
              size="md"
            />
          </div>
        </Link>
      ))}
    </div>
  );
}

function EarningsTab({
  folderId,
  tickers,
  earnings,
  isLoading,
}: {
  folderId: string;
  tickers: string[];
  earnings: import('../types').Earnings[];
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <EarningsTable
      folderId={folderId}
      tickers={tickers}
      earnings={earnings}
    />
  );
}

function GuidanceTab({
  folderId,
  tickers,
}: {
  folderId: string;
  tickers: string[];
}) {
  return (
    <GuidanceTable
      folderId={folderId}
      tickers={tickers}
    />
  );
}

function AttachmentsTab({
  folderId,
  attachments,
  isLoading,
}: {
  folderId: string;
  attachments: Attachment[];
  isLoading: boolean;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const uploadMutation = useMutation({
    mutationFn: (file: File) => attachmentsApi.uploadToFolder(folderId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folder-attachments', folderId] });
      addToast('success', 'File uploaded');
    },
    onError: () => {
      addToast('error', 'Failed to upload file');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: attachmentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folder-attachments', folderId] });
      addToast('success', 'File deleted');
    },
  });

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <label className="btn-primary cursor-pointer">
          <Upload className="mr-2 h-4 w-4" />
          Upload File
          <input
            type="file"
            onChange={handleUpload}
            className="hidden"
          />
        </label>
      </div>

      {attachments.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <Paperclip className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No attachments</h3>
          <p className="mt-2 text-sm text-gray-500">
            Upload Excel files, PDFs, or images.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="card flex items-center justify-between p-3"
            >
              <div>
                <p className="font-medium text-gray-900">{attachment.filename}</p>
                <p className="text-sm text-gray-500">
                  {(attachment.size_bytes / 1024).toFixed(1)} KB ·{' '}
                  {format(new Date(attachment.uploaded_at), 'MMM d, yyyy')}
                </p>
              </div>
              <div className="flex gap-2">
                <a
                  href={attachmentsApi.download(attachment.id)}
                  className="btn-secondary"
                >
                  <Download className="h-4 w-4" />
                </a>
                <button
                  onClick={() => deleteMutation.mutate(attachment.id)}
                  className="btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function PerformanceTab({
  folderId,
  themeDate,
}: {
  folderId: string;
  themeDate: string;
}) {
  return <ThemePerformance folderId={folderId} themeDate={themeDate} />;
}

function NotesTab({ folderId }: { folderId: string }) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [isNoteModalOpen, setIsNoteModalOpen] = useState(false);

  const { data: notes, isLoading } = useQuery({
    queryKey: ['folder-notes', folderId],
    queryFn: () => notesApi.listForFolder(folderId),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Notes</h2>
        <button
          onClick={() => setIsNoteModalOpen(true)}
          className="btn-primary"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Note
        </button>
      </div>

      {notes && notes.length > 0 ? (
        <div className="space-y-3">
          {notes.map((note) => (
            <FolderNoteCard key={note.id} note={note} folderId={folderId} />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No notes yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Add notes to track your thoughts on this theme.
          </p>
          <button
            onClick={() => setIsNoteModalOpen(true)}
            className="btn-primary mt-4"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Note
          </button>
        </div>
      )}

      <AddFolderNoteModal
        isOpen={isNoteModalOpen}
        onClose={() => setIsNoteModalOpen(false)}
        folderId={folderId}
      />
    </div>
  );
}

function FolderNoteCard({
  note,
  folderId,
}: {
  note: Note;
  folderId: string;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const deleteMutation = useMutation({
    mutationFn: () => notesApi.delete(note.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folder-notes', folderId] });
      addToast('success', 'Note deleted');
    },
  });

  return (
    <div className="card p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="badge-gray text-xs">{note.note_type}</span>
            <span className="text-xs text-gray-400">
              {format(new Date(note.created_at), 'MMM d, yyyy h:mm a')}
            </span>
          </div>
          <div className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
            {note.content_md}
          </div>
        </div>
        <button
          onClick={() => {
            if (confirm('Delete this note?')) {
              deleteMutation.mutate();
            }
          }}
          className="text-gray-400 hover:text-red-500"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function AddFolderNoteModal({
  isOpen,
  onClose,
  folderId,
}: {
  isOpen: boolean;
  onClose: () => void;
  folderId: string;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [noteType, setNoteType] = useState<NoteType>('GENERAL');
  const [content, setContent] = useState('');

  const createMutation = useMutation({
    mutationFn: () =>
      notesApi.create({
        folder_id: folderId,
        note_type: noteType,
        content_md: content,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folder-notes', folderId] });
      addToast('success', 'Note added');
      onClose();
      setContent('');
      setNoteType('GENERAL');
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
          <label className="label mb-1">Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="input font-mono text-sm"
            required
            placeholder="Add your notes here..."
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
