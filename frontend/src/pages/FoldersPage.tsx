import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, FolderOpen, Trash2 } from 'lucide-react';
import { foldersApi } from '../api/folders';
import { Modal } from '../components/ui/Modal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useToast } from '../components/ui/Toast';
import type { FolderCreate, FolderType, TickerPnL } from '../types';

export function FoldersPage() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['folders', searchTerm],
    queryFn: () => foldersApi.list(searchTerm || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: foldersApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      addToast('success', 'Folder deleted');
    },
    onError: () => {
      addToast('error', 'Failed to delete folder');
    },
  });

  const handleDelete = (id: string, name: string) => {
    if (confirm(`Delete folder "${name}" and all its contents?`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Folders</h1>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Folder
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by ticker..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Folders Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : data?.folders.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <FolderOpen className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No folders yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Get started by creating your first folder.
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn-primary mt-4"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Folder
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.folders.map((folder) => (
            <div key={folder.id} className="card p-4">
              <div className="flex items-start justify-between">
                <Link
                  to={`/folders/${folder.id}`}
                  className="flex-1"
                >
                  <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-600">
                    {folder.name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {folder.type === 'PAIR' ? 'Pair Trade' : folder.type === 'THEME' ? 'Theme' : 'Single Ticker'}
                  </p>
                </Link>
                <button
                  onClick={() => handleDelete(folder.id, folder.name)}
                  className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="mt-4 flex items-center gap-4 text-sm">
                <span className="text-gray-500">
                  {folder.idea_count} idea{folder.idea_count !== 1 ? 's' : ''}
                </span>
                {folder.active_idea_count > 0 && (
                  <span className="badge-green">
                    {folder.active_idea_count} active
                  </span>
                )}
              </div>

              {folder.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {folder.tags.map((tag) => (
                    <span key={tag} className="badge-gray">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <CreateFolderModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
}

function CreateFolderModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [folderType, setFolderType] = useState<FolderType>('SINGLE');
  const [tickerPrimary, setTickerPrimary] = useState('');
  const [tickerSecondary, setTickerSecondary] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');

  // THEME fields
  const [themeName, setThemeName] = useState('');
  const [themeDate, setThemeDate] = useState('');
  const [themeThesis, setThemeThesis] = useState('');
  const [themeTickers, setThemeTickers] = useState<TickerPnL[]>([]);
  const [newTicker, setNewTicker] = useState('');
  const [newPnl, setNewPnl] = useState('');

  const createMutation = useMutation({
    mutationFn: foldersApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      addToast('success', 'Folder created');
      onClose();
      resetForm();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      addToast('error', error.response?.data?.detail || 'Failed to create folder');
    },
  });

  const resetForm = () => {
    setFolderType('SINGLE');
    setTickerPrimary('');
    setTickerSecondary('');
    setDescription('');
    setTags('');
    setThemeName('');
    setThemeDate('');
    setThemeThesis('');
    setThemeTickers([]);
    setNewTicker('');
    setNewPnl('');
  };

  const addTickerToTheme = () => {
    if (newTicker.trim()) {
      const ticker: TickerPnL = {
        ticker: newTicker.toUpperCase().trim(),
        pnl: newPnl ? parseFloat(newPnl) : undefined,
      };
      setThemeTickers([...themeTickers, ticker]);
      setNewTicker('');
      setNewPnl('');
    }
  };

  const removeTickerFromTheme = (index: number) => {
    setThemeTickers(themeTickers.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const data: FolderCreate = {
      type: folderType,
      ticker_primary: folderType !== 'THEME' ? tickerPrimary.toUpperCase() : undefined,
      ticker_secondary: folderType === 'PAIR' ? tickerSecondary.toUpperCase() : undefined,
      theme_name: folderType === 'THEME' ? themeName : undefined,
      theme_date: folderType === 'THEME' && themeDate ? themeDate : undefined,
      theme_thesis: folderType === 'THEME' && themeThesis ? themeThesis : undefined,
      theme_tickers: folderType === 'THEME' ? themeTickers : undefined,
      description: description || undefined,
      tags: tags
        ? tags.split(',').map((t) => t.trim()).filter(Boolean)
        : [],
    };

    createMutation.mutate(data);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Folder">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label mb-1">Folder Type</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="SINGLE"
                checked={folderType === 'SINGLE'}
                onChange={(e) => setFolderType(e.target.value as FolderType)}
                className="mr-2"
              />
              Single Ticker
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="PAIR"
                checked={folderType === 'PAIR'}
                onChange={(e) => setFolderType(e.target.value as FolderType)}
                className="mr-2"
              />
              Pair Trade
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="THEME"
                checked={folderType === 'THEME'}
                onChange={(e) => setFolderType(e.target.value as FolderType)}
                className="mr-2"
              />
              Theme
            </label>
          </div>
        </div>

        {folderType === 'THEME' ? (
          <>
            <div>
              <label htmlFor="themeName" className="label mb-1">
                Theme Name *
              </label>
              <input
                id="themeName"
                type="text"
                value={themeName}
                onChange={(e) => setThemeName(e.target.value)}
                placeholder="e.g., AI Infrastructure"
                className="input"
                required
              />
            </div>

            <div>
              <label htmlFor="themeDate" className="label mb-1">
                Theme Date (optional)
              </label>
              <input
                id="themeDate"
                type="date"
                value={themeDate}
                onChange={(e) => setThemeDate(e.target.value)}
                className="input"
              />
            </div>

            <div>
              <label htmlFor="themeThesis" className="label mb-1">
                Theme Thesis (optional)
              </label>
              <textarea
                id="themeThesis"
                value={themeThesis}
                onChange={(e) => setThemeThesis(e.target.value)}
                rows={4}
                className="input"
                placeholder="Investment thesis and rationale..."
              />
            </div>

            <div>
              <label className="label mb-1">Theme Tickers</label>
              {themeTickers.length > 0 && (
                <div className="mb-3 space-y-2">
                  {themeTickers.map((ticker, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded border border-gray-300 bg-gray-50 px-3 py-2"
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-gray-900">
                          {ticker.ticker}
                        </span>
                        {ticker.pnl !== undefined && (
                          <span
                            className={`text-sm ${
                              ticker.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {ticker.pnl >= 0 ? '+' : ''}
                            {ticker.pnl.toFixed(1)}%
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeTickerFromTheme(index)}
                        className="text-sm text-red-600 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTicker}
                  onChange={(e) => setNewTicker(e.target.value)}
                  placeholder="Ticker"
                  className="input flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addTickerToTheme();
                    }
                  }}
                />
                <input
                  type="number"
                  step="0.1"
                  value={newPnl}
                  onChange={(e) => setNewPnl(e.target.value)}
                  placeholder="P&L %"
                  className="input w-24"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addTickerToTheme();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={addTickerToTheme}
                  className="btn-secondary"
                >
                  Add
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            <div>
              <label htmlFor="tickerPrimary" className="label mb-1">
                {folderType === 'PAIR' ? 'Primary Ticker' : 'Ticker'}
              </label>
              <input
                id="tickerPrimary"
                type="text"
                value={tickerPrimary}
                onChange={(e) => setTickerPrimary(e.target.value)}
                placeholder="e.g., AAPL"
                className="input"
                required
              />
            </div>

            {folderType === 'PAIR' && (
              <div>
                <label htmlFor="tickerSecondary" className="label mb-1">
                  Secondary Ticker
                </label>
                <input
                  id="tickerSecondary"
                  type="text"
                  value={tickerSecondary}
                  onChange={(e) => setTickerSecondary(e.target.value)}
                  placeholder="e.g., MSFT"
                  className="input"
                  required
                />
              </div>
            )}
          </>
        )}

        <div>
          <label htmlFor="description" className="label mb-1">
            Description (optional)
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="input"
          />
        </div>

        <div>
          <label htmlFor="tags" className="label mb-1">
            Tags (comma-separated)
          </label>
          <input
            id="tags"
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g., tech, growth"
            className="input"
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
            {createMutation.isPending ? 'Creating...' : 'Create Folder'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
