// Enums
export type FolderType = 'SINGLE' | 'PAIR' | 'THEME';
export type TradeType = 'LONG' | 'SHORT' | 'PAIR_LONG_SHORT';
export type PairOrientation = 'LONG_PRIMARY_SHORT_SECONDARY' | 'SHORT_PRIMARY_LONG_SECONDARY';
export type IdeaStatus = 'DRAFT' | 'ACTIVE' | 'SCALED_UP' | 'TRIMMED' | 'CLOSED' | 'KILLED';
export type Horizon = 'EVENT' | '3_6MO' | '6_12MO' | 'SECULAR' | 'OTHER';
export type NoteType = 'GENERAL' | 'EARNINGS' | 'CHANNEL_CHECK' | 'VALUATION' | 'RISK' | 'POSTMORTEM';
export type PriceSource = 'YFINANCE' | 'MANUAL';

// User
export interface User {
  id: string;
  username: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

// Auth
export interface AuthStatus {
  setup_required: boolean;
  authenticated: boolean;
  user: User | null;
}

// Folder
export interface TickerPnL {
  ticker: string;
  pnl?: number;
}

export interface Folder {
  id: string;
  type: FolderType;

  // SINGLE/PAIR fields
  ticker_primary: string | null;
  ticker_secondary: string | null;

  // THEME fields
  theme_name: string | null;
  theme_date: string | null;
  theme_thesis: string | null;
  theme_tickers: TickerPnL[];

  // Theme associations
  theme_ids: string[];

  // Common fields
  name: string;
  description: string | null;
  tags: string[];
  tickers: string[];
  created_at: string;
  updated_at: string;
  idea_count: number;
  active_idea_count: number;
}

export interface FolderCreate {
  type: FolderType;

  // SINGLE/PAIR fields
  ticker_primary?: string;
  ticker_secondary?: string;

  // THEME fields
  theme_name?: string;
  theme_date?: string;
  theme_thesis?: string;
  theme_tickers?: TickerPnL[];

  // Common fields
  description?: string;
  tags?: string[];
}

export interface ThemeOption {
  id: string;
  name: string;
  date: string | null;
  ticker_count: number;
}

export interface ThemeTickerPerformance {
  ticker: string;
  start_price: number | null;
  current_price: number | null;
  pnl_percent: number | null;
}

// Idea
export interface Idea {
  id: string;
  folder_id: string;
  title: string;
  trade_type: TradeType;
  pair_orientation: PairOrientation | null;
  status: IdeaStatus;
  start_date: string;
  entry_price_primary: number;
  entry_price_secondary: number | null;
  position_size: number;
  horizon: Horizon;
  thesis_md: string | null;
  catalysts: string[];
  risks: string[];
  kill_criteria_md: string | null;
  target_price_primary: number | null;
  stop_level_primary: number | null;
  target_price_secondary: number | null;
  stop_level_secondary: number | null;
  exit_price_primary: number | null;
  exit_price_secondary: number | null;
  exit_date: string | null;
  created_at: string;
  updated_at: string;
  current_price_primary: number | null;
  current_price_secondary: number | null;
  pnl_percent: number | null;
  pnl_absolute: number | null;
  folder_name: string | null;
}

export interface IdeaCreate {
  folder_id: string;
  title: string;
  trade_type: TradeType;
  pair_orientation?: PairOrientation;
  start_date: string;
  entry_price_primary: number;
  entry_price_secondary?: number;
  position_size?: number;
  horizon?: Horizon;
  thesis_md?: string;
  catalysts?: string[];
  risks?: string[];
  kill_criteria_md?: string;
  target_price_primary?: number;
  stop_level_primary?: number;
  target_price_secondary?: number;
  stop_level_secondary?: number;
}

export interface CloseIdeaRequest {
  status: 'CLOSED' | 'KILLED';
  exit_price_primary: number;
  exit_price_secondary?: number;
  exit_date: string;
  postmortem_note?: string;
}

// Note
export interface Note {
  id: string;
  idea_id: string | null;
  folder_id: string | null;
  note_type: NoteType;
  content_md: string;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  idea_id?: string;
  folder_id?: string;
  note_type: NoteType;
  content_md: string;
}

// Attachment
export interface Attachment {
  id: string;
  folder_id: string | null;
  idea_id: string | null;
  filename: string;
  mime_type: string;
  size_bytes: number;
  uploaded_at: string;
}

// Price Snapshot
export interface PriceSnapshot {
  id: string;
  idea_id: string;
  timestamp: string;
  price_primary: number;
  price_secondary: number | null;
  source: PriceSource;
  note: string | null;
}

export interface PriceSnapshotCreate {
  timestamp: string;
  price_primary: number;
  price_secondary?: number;
  note?: string;
}

// Earnings
export type PeriodType = 'QUARTERLY' | 'ANNUAL';
export type MetricType = 'EPS' | 'REVENUE' | 'EBITDA' | 'FCF';

export interface Earnings {
  id: string;
  folder_id: string;
  ticker: string;
  period_type: PeriodType;
  period: string | null;
  fiscal_quarter: string;
  period_end_date: string | null;
  // Consensus estimates
  estimate_eps: number | null;
  actual_eps: number | null;
  estimate_rev: number | null;
  actual_rev: number | null;
  estimate_ebitda: number | null;
  actual_ebitda: number | null;
  estimate_fcf: number | null;
  actual_fcf: number | null;
  // User's own estimates
  my_estimate_eps: number | null;
  my_estimate_rev: number | null;
  my_estimate_ebitda: number | null;
  my_estimate_fcf: number | null;
  // Surprise calculations
  eps_surprise: number | null;
  eps_surprise_pct: number | null;
  rev_surprise: number | null;
  rev_surprise_pct: number | null;
  ebitda_surprise_pct: number | null;
  fcf_surprise_pct: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface EarningsCreate {
  folder_id: string;
  ticker: string;
  period_type?: PeriodType;
  period?: string;
  fiscal_quarter: string;
  period_end_date?: string;
  // Consensus estimates
  estimate_eps?: number;
  actual_eps?: number;
  estimate_rev?: number;
  actual_rev?: number;
  estimate_ebitda?: number;
  actual_ebitda?: number;
  estimate_fcf?: number;
  actual_fcf?: number;
  // User's own estimates
  my_estimate_eps?: number;
  my_estimate_rev?: number;
  my_estimate_ebitda?: number;
  my_estimate_fcf?: number;
  notes?: string;
}

export interface Guidance {
  id: string;
  folder_id: string;
  ticker: string;
  period: string;
  metric: MetricType | 'OTHER';
  guidance_period: string;
  guidance_low: number | null;
  guidance_high: number | null;
  guidance_point: number | null;
  actual_result: number | null;
  guidance_midpoint: number | null;
  vs_guidance_low: number | null;
  vs_guidance_high: number | null;
  vs_guidance_midpoint: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface GuidanceCreate {
  folder_id: string;
  ticker: string;
  period: string;
  metric: MetricType | 'OTHER';
  guidance_period: string;
  guidance_low?: number;
  guidance_high?: number;
  guidance_point?: number;
  actual_result?: number;
  notes?: string;
}

// P&L
export interface PnLResponse {
  idea_id: string;
  trade_type: TradeType;
  is_realized: boolean;
  entry_price_primary: number;
  entry_price_secondary: number | null;
  current_price_primary: number;
  current_price_secondary: number | null;
  pnl_percent: number;
  pnl_absolute: number | null;
  pnl_primary_leg: number | null;
  pnl_secondary_leg: number | null;
  simple_spread: number | null;
  price_timestamp: string | null;
}

export interface PnLHistoryPoint {
  timestamp: string;
  price_primary: number;
  price_secondary: number | null;
  pnl_percent: number;
  pnl_primary_leg: number | null;
  pnl_secondary_leg: number | null;
}

export interface PnLHistoryResponse {
  idea_id: string;
  trade_type: TradeType;
  entry_price_primary: number;
  entry_price_secondary: number | null;
  history: PnLHistoryPoint[];
}

// API Response types
export interface FolderListResponse {
  folders: Folder[];
  total: number;
}

export interface IdeaListResponse {
  ideas: Idea[];
  total: number;
}

export interface EarningsListResponse {
  earnings: Earnings[];
  total: number;
}

export interface GuidanceListResponse {
  guidance: Guidance[];
  total: number;
}

export interface BackfillResponse {
  idea_id: string;
  snapshots_created: number;
  start_date: string;
  end_date: string;
  message: string;
}
