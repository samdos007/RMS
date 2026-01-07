import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { notesApi } from '../api/notes';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { NoteType } from '../types';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [noteType, setNoteType] = useState<NoteType | ''>('');
  const [searchTerm, setSearchTerm] = useState('');

  const { data: notes, isLoading } = useQuery({
    queryKey: ['search-notes', searchTerm, noteType],
    queryFn: () =>
      notesApi.search(searchTerm, undefined, noteType || undefined),
    enabled: searchTerm.length > 0,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchTerm(query);
  };

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Search Notes</h1>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search notes..."
              className="input pl-10"
            />
          </div>

          <select
            value={noteType}
            onChange={(e) => setNoteType(e.target.value as NoteType | '')}
            className="input w-40"
          >
            <option value="">All Types</option>
            <option value="GENERAL">General</option>
            <option value="EARNINGS">Earnings</option>
            <option value="CHANNEL_CHECK">Channel Check</option>
            <option value="VALUATION">Valuation</option>
            <option value="RISK">Risk</option>
            <option value="POSTMORTEM">Post-Mortem</option>
          </select>

          <button type="submit" className="btn-primary">
            Search
          </button>
        </div>
      </form>

      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {!isLoading && searchTerm && notes?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No notes found for "{searchTerm}"</p>
        </div>
      )}

      {notes && notes.length > 0 && (
        <div className="space-y-4">
          {notes.map((note) => (
            <Link
              key={note.id}
              to={`/ideas/${note.idea_id}`}
              className="card block p-4 hover:bg-gray-50"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="badge-gray text-xs">{note.note_type}</span>
                <span className="text-sm text-gray-500">
                  {format(new Date(note.created_at), 'MMM d, yyyy')}
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-gray-600 line-clamp-3">
                <ReactMarkdown>{note.content_md}</ReactMarkdown>
              </div>
            </Link>
          ))}
        </div>
      )}

      {!searchTerm && (
        <div className="text-center py-12">
          <Search className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-gray-500">
            Enter a search term to find notes across all ideas
          </p>
        </div>
      )}
    </div>
  );
}
