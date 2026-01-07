import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, Plus } from 'lucide-react';
import { foldersApi } from '../../api/folders';
import type { ThemeOption } from '../../types';

interface ThemeSelectorProps {
  selectedThemes: string[];
  onSelectionChange: (themeIds: string[]) => void;
}

export function ThemeSelector({ selectedThemes, onSelectionChange }: ThemeSelectorProps) {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { data: themes = [] } = useQuery({
    queryKey: ['themes', 'autocomplete', search],
    queryFn: () => foldersApi.autocompleteThemes(search || undefined),
    enabled: isOpen,
  });

  // Get selected theme details for display
  const { data: allThemes = [] } = useQuery({
    queryKey: ['themes', 'autocomplete'],
    queryFn: () => foldersApi.autocompleteThemes(),
  });

  const selectedThemeObjects = allThemes.filter((t) =>
    selectedThemes.includes(t.id)
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const addTheme = (theme: ThemeOption) => {
    if (!selectedThemes.includes(theme.id)) {
      onSelectionChange([...selectedThemes, theme.id]);
    }
    setSearch('');
    setIsOpen(false);
  };

  const removeTheme = (themeId: string) => {
    onSelectionChange(selectedThemes.filter((id) => id !== themeId));
  };

  const filteredThemes = themes.filter(
    (theme) => !selectedThemes.includes(theme.id)
  );

  return (
    <div className="space-y-2">
      <label className="label">Associated Themes</label>

      {/* Selected themes badges */}
      {selectedThemeObjects.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedThemeObjects.map((theme) => (
            <div
              key={theme.id}
              className="flex items-center gap-2 rounded-full bg-primary-100 px-3 py-1 text-sm text-primary-800"
            >
              <span>{theme.name}</span>
              <button
                type="button"
                onClick={() => removeTheme(theme.id)}
                className="rounded-full hover:bg-primary-200"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Autocomplete dropdown */}
      <div className="relative" ref={dropdownRef}>
        <div className="relative">
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder="Search themes to add..."
            className="input pr-10"
          />
          <Plus className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
        </div>

        {isOpen && filteredThemes.length > 0 && (
          <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-300 bg-white shadow-lg">
            {filteredThemes.map((theme) => (
              <button
                key={theme.id}
                type="button"
                onClick={() => addTheme(theme)}
                className="w-full px-4 py-2 text-left hover:bg-gray-100"
              >
                <div className="flex items-baseline justify-between">
                  <span className="font-medium text-gray-900">{theme.name}</span>
                  <span className="text-xs text-gray-500">
                    {theme.ticker_count} ticker{theme.ticker_count !== 1 ? 's' : ''}
                  </span>
                </div>
                {theme.date && (
                  <div className="text-xs text-gray-500">
                    {new Date(theme.date).toLocaleDateString()}
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
