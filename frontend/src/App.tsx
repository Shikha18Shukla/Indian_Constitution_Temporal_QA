import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import {
  Activity, ArrowDown, ArrowRight, BookOpen, CalendarDays, Check, ChevronDown,
  CircleAlert, Clock3, Command, Download, FileText, History,
  Landmark, LoaderCircle, MessageSquareText, Network, PanelTop, Scale, ShieldCheck,
  Sparkles, TriangleAlert, Wifi, WifiOff,
} from 'lucide-react'
import { api } from './lib/api'
import type { ComparisonRun, Evidence, HealthResponse, SystemId, SystemResult } from './types'

const SYSTEMS: Array<{
  id: SystemId
  shortName: string
  name: string
  description: string
  detail: string
  icon: typeof Sparkles
  tone: string
}> = [
  { id: 'A', shortName: 'Base LLM', name: 'System A', description: 'Parametric answer', detail: 'No project retrieval or corpus context', icon: Sparkles, tone: 'violet' },
  { id: 'B', shortName: 'Static RAG', name: 'System B', description: 'Fixed corpus retrieval', detail: 'Searches the same static index for every date', icon: Network, tone: 'blue' },
  { id: 'C', shortName: 'Temporal RAG', name: 'System C', description: 'Version-aware retrieval', detail: 'Selects verified Article text for the reference date', icon: Clock3, tone: 'teal' },
]

const DEFAULT_QUESTION = 'What powers did the Governor have under Article 174?'
const DEFAULT_DATE = '2026-05-01'

function classNames(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

function statusPresentation(result: SystemResult) {
  if (result.status === 'completed') return { label: 'Answer returned', style: 'status-completed', icon: Check }
  if (result.status === 'abstained') return { label: 'Abstained', style: 'status-abstained', icon: ShieldCheck }
  return { label: 'Request error', style: 'status-failed', icon: CircleAlert }
}

function elapsedLabel(seconds: number) {
  if (seconds < 1) return `${Math.round(seconds * 1000)} ms`
  return `${seconds.toFixed(1)} s`
}

function dateLabel(value: string) {
  const parsed = new Date(`${value}T00:00:00`)
  return Number.isNaN(parsed.getTime()) ? value : new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(parsed)
}

function sourceLabel(evidence: Evidence) {
  const document = evidence.source_document || 'Source document'
  const locator = evidence.source_locator || (evidence.page_number ? `Page ${evidence.page_number}` : '')
  return [document, locator].filter(Boolean).join(' · ')
}

const MISSING_PROVENANCE = 'Not available in source metadata'

function provenanceValue(value: unknown): string {
  return typeof value === 'string' && value.trim() ? value : MISSING_PROVENANCE
}

function citationPage(evidence: Evidence | null): string {
  if (!evidence) return MISSING_PROVENANCE
  if (evidence.page_number !== undefined && evidence.page_number !== null && String(evidence.page_number).trim()) {
    return `PDF page ${evidence.page_number}`
  }
  const locator = evidence.source_locator
  if (typeof locator === 'string') {
    const match = locator.match(/PDF\s+(?:page|p\.?\s*)(\d+)/i)
    if (match) return `PDF page ${match[1]} (from recorded locator)`
  }
  return MISSING_PROVENANCE
}

function CitationDisclosure({ citation }: { citation: SystemResult['citations'][number] }) {
  const evidence = citation.evidence
  const passage = evidence?.chunk_text || evidence?.text
  const articleOrSection = evidence?.article_number
    ? `Article ${evidence.article_number}`
    : evidence?.source_section || evidence?.section_or_heading
  const version = evidence?.version_id
  const legalInterval = evidence?.effective_from
    ? `[${evidence.effective_from}, ${evidence.effective_to ?? 'null'})`
    : undefined
  const coverage = evidence?.evidence_coverage?.verified_through || evidence?.evidence_verified_through

  return (
    <details className="citation-disclosure">
      <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2.5 marker:hidden">
        <span className={classNames('citation-chip', citation.found_in_retrieved_evidence ? 'citation-found' : 'citation-unresolved')}>
          {citation.found_in_retrieved_evidence ? <Check size={12} /> : <TriangleAlert size={12} />}{citation.citation_id}
        </span>
        <span className={classNames('text-[10px] font-bold', citation.found_in_retrieved_evidence ? 'text-emerald-700' : 'text-amber-700')}>
          {citation.found_in_retrieved_evidence ? 'Passage resolved' : 'No matching retrieved passage'}
        </span>
        <ChevronDown className="ml-auto shrink-0 text-slate-400 transition group-open:rotate-180" size={15} />
      </summary>
      <div className="space-y-3 border-t border-slate-100 px-3 pb-4 pt-3">
        <ProvenanceRow label="Citation / chunk ID" value={citation.citation_id} />
        <ProvenanceRow label="Source document" value={evidence?.source_document} />
        <ProvenanceRow label="Article or section" value={articleOrSection} />
        <ProvenanceRow label="PDF page number" value={citationPage(evidence)} />
        <div><p className="provenance-label">Retrieved passage</p>{passage ? <p className="mt-1 whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs leading-5 text-slate-700">{passage}</p> : <p className="mt-1 text-xs text-slate-500">{MISSING_PROVENANCE}</p>}</div>
        <ProvenanceRow label="Temporal version ID" value={version} />
        <ProvenanceRow label="Effective interval" value={legalInterval} />
        <ProvenanceRow label="Evidence coverage (inclusive)" value={coverage} />
        {!citation.found_in_retrieved_evidence && <p className="rounded-lg bg-amber-50 px-3 py-2 text-[11px] leading-5 text-amber-900">This citation identifier appeared in the answer, but the API returned no matching passage for this run.</p>}
      </div>
    </details>
  )
}

function ProvenanceRow({ label, value }: { label: string; value: unknown }) {
  return <div><p className="provenance-label">{label}</p><p className="mt-0.5 break-words text-xs leading-5 text-slate-700">{provenanceValue(value)}</p></div>
}

function SystemOverviewCard({ system, available }: { system: (typeof SYSTEMS)[number]; available?: boolean }) {
  const Icon = system.icon
  return (
    <article className="group rounded-2xl border border-slate-200/80 bg-white p-4 shadow-[0_2px_8px_rgba(22,36,63,.035)] transition hover:-translate-y-0.5 hover:shadow-[0_12px_30px_rgba(22,36,63,.08)] sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div className={classNames('flex h-10 w-10 items-center justify-center rounded-xl', `tone-${system.tone}`)}>
          <Icon size={19} strokeWidth={1.8} />
        </div>
        {available === undefined ? <span className="availability-label"><span className="h-1.5 w-1.5 rounded-full bg-slate-300" /> System</span> : (
          <span className={classNames('availability-label', available ? 'text-emerald-700' : 'text-amber-700')}>
            <span className={classNames('h-1.5 w-1.5 rounded-full', available ? 'bg-emerald-500' : 'bg-amber-500')} />
            {available ? 'Available' : 'Unavailable'}
          </span>
        )}
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <h2 className="display-font text-[15px] font-extrabold tracking-[-.025em] text-slate-900">{system.name}</h2>
        <span className="text-xs font-medium text-slate-400">{system.shortName}</span>
      </div>
      <p className="mt-1 text-[13px] font-semibold text-slate-700">{system.description}</p>
      <p className="mt-1 text-xs leading-5 text-slate-500">{system.detail}</p>
    </article>
  )
}

function StatusBadge({ result }: { result: SystemResult }) {
  const status = statusPresentation(result)
  const Icon = status.icon
  return <span className={classNames('status-badge', status.style)}><Icon size={13} />{status.label}</span>
}

function EvidenceItem({ evidence, index, context = false }: { evidence: Evidence; index: number; context?: boolean }) {
  const text = typeof evidence.chunk_text === 'string' ? evidence.chunk_text : typeof evidence.text === 'string' ? evidence.text : ''
  return (
    <details className="evidence-item group">
      <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-3.5 marker:hidden">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-[11px] font-bold text-slate-600">{index + 1}</span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-semibold text-slate-800">{evidence.chunk_id || evidence.version_id || 'Evidence passage'}</p>
          <p className="mt-0.5 truncate text-[11px] text-slate-500">{sourceLabel(evidence) || 'Source details are not available'}</p>
        </div>
        {context && <span className="hidden rounded-md bg-indigo-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-indigo-700 sm:inline">In prompt</span>}
        {typeof evidence.retrieval_score === 'number' && <span className="hidden tabular-nums text-[10px] text-slate-400 md:inline">{evidence.retrieval_score.toFixed(3)}</span>}
        <ChevronDown className="shrink-0 text-slate-400 transition group-open:rotate-180" size={15} />
      </summary>
      <div className="border-t border-slate-100 px-4 pb-4 pt-3">
        {text ? <p className="whitespace-pre-wrap text-[13px] leading-6 text-slate-700">{text}</p> : <p className="text-xs italic text-slate-500">Passage text was not included in this record.</p>}
        <div className="mt-3 flex flex-wrap gap-2">
          {evidence.article_number && <MetaPill>Article {evidence.article_number}</MetaPill>}
          {evidence.version_id && <MetaPill>Version {evidence.version_id}</MetaPill>}
          {evidence.verification_status && <MetaPill>{evidence.verification_status}</MetaPill>}
          {evidence.effective_from && <MetaPill>{evidence.effective_from} – {evidence.effective_to || 'open legal interval'}</MetaPill>}
        </div>
      </div>
    </details>
  )
}

function MetaPill({ children }: { children: ReactNode }) {
  return <span className="rounded-md border border-slate-200 bg-white px-2 py-1 text-[10px] font-medium text-slate-600">{children}</span>
}

function TemporalDetails({ result }: { result: SystemResult }) {
  if (result.system !== 'C') return null
  return (
    <div className="mt-4 rounded-xl border border-teal-100 bg-teal-50/65 p-4">
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.08em] text-teal-800"><Clock3 size={14} /> Temporal selection</div>
      {result.selected_version_ids.length ? (
        <div className="mt-3 space-y-3">
          {result.effective_dates.map((interval) => (
            <div key={interval.version_id} className="rounded-lg border border-teal-100 bg-white/80 p-3">
              <p className="text-xs font-bold text-slate-800">{interval.version_id}</p>
              <div className="mt-2 grid gap-2 text-[11px] sm:grid-cols-2">
                <div><span className="text-slate-500">Legal interval</span><p className="mt-0.5 font-semibold text-slate-700">[{interval.effective_from}, {interval.effective_to || '∞'})</p></div>
                <div><span className="text-slate-500">Evidence supported through</span><p className="mt-0.5 font-semibold text-slate-700">{interval.evidence_verified_through || 'Not recorded'}</p></div>
              </div>
            </div>
          ))}
          <p className="text-[11px] text-teal-900/80">Legal intervals are half-open; evidence cutoffs are inclusive.</p>
        </div>
      ) : (
        <p className="mt-3 text-xs leading-5 text-slate-600">No verified Article version was selected for this request.</p>
      )}
      {result.abstention_reason && <div className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-900"><span className="font-bold">Abstention reason:</span> {result.abstention_reason}</div>}
    </div>
  )
}

function ResultCard({ system, result }: { system: (typeof SYSTEMS)[number]; result: SystemResult }) {
  const Icon = system.icon
  const [showEvidence, setShowEvidence] = useState(false)
  const usedEvidenceIds = useMemo(() => new Set(result.prompt_evidence.map((evidence) => evidence.chunk_id)), [result.prompt_evidence])
  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_4px_20px_rgba(22,36,63,.045)]">
      <header className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-4 sm:px-5">
        <div className="flex min-w-0 items-center gap-3">
          <span className={classNames('flex h-9 w-9 shrink-0 items-center justify-center rounded-xl', `tone-${system.tone}`)}><Icon size={17} /></span>
          <div className="min-w-0">
            <div className="flex flex-wrap items-baseline gap-x-2"><h3 className="display-font text-sm font-extrabold text-slate-900">{system.name}</h3><span className="text-[11px] text-slate-400">{system.shortName}</span></div>
            <p className="mt-0.5 text-[11px] text-slate-500">{result.model_name || 'Gemini generation model'}</p>
          </div>
        </div>
        <StatusBadge result={result} />
      </header>
      <div className="p-4 sm:p-5">
        <div className="flex items-center gap-2 text-[11px] font-medium text-slate-500"><Clock3 size={13} />{elapsedLabel(result.elapsed_seconds)} total</div>
        {result.status === 'completed' && result.answer ? (
          <div className="answer-panel mt-3"><p className="whitespace-pre-wrap text-[13px] leading-6 text-slate-800">{result.answer}</p></div>
        ) : result.status === 'abstained' ? (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3.5"><p className="text-xs font-bold text-amber-900">System abstained</p><p className="mt-1 whitespace-pre-wrap text-[13px] leading-6 text-amber-900/90">{result.answer || 'No answer was returned.'}</p>{result.abstention_reason && <p className="mt-2 text-[11px] text-amber-800">Reason: {result.abstention_reason}</p>}</div>
        ) : (
          <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3.5"><p className="text-xs font-bold text-rose-900">This system did not return an answer.</p><p className="mt-1 whitespace-pre-wrap break-words text-[12px] leading-5 text-rose-800">{result.error || 'No error detail was recorded.'}</p></div>
        )}

        {result.citations.length > 0 && <div className="mt-4"><p className="section-label"><FileText size={13} /> Citations</p><div className="mt-2 divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200">{result.citations.map((citation) => <CitationDisclosure key={citation.citation_id} citation={citation} />)}</div></div>}
        {result.retrieved_evidence.length > 0 && (
          <div className="mt-4">
            <button className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-3.5 py-3 text-left hover:bg-slate-50" onClick={() => setShowEvidence(!showEvidence)}>
              <span><span className="block text-xs font-bold text-slate-800">Retrieved evidence</span><span className="mt-0.5 block text-[11px] text-slate-500">{result.retrieved_evidence.length} passages · {result.prompt_evidence.length} sent to generation</span></span>
              <ChevronDown className={classNames('text-slate-400 transition', showEvidence && 'rotate-180')} size={16} />
            </button>
            {showEvidence && <div className="mt-2 divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200">{result.retrieved_evidence.map((evidence, index) => <EvidenceItem key={evidence.chunk_id || `${index}`} evidence={evidence} index={index} context={usedEvidenceIds.has(evidence.chunk_id)} />)}</div>}
          </div>
        )}
        {result.retrieved_evidence.length === 0 && result.retrieval_used && <p className="mt-4 text-xs text-slate-500">Retrieval was used, but no passage details were returned.</p>}
        <TemporalDetails result={result} />
        {(result.retrieval_elapsed_seconds != null || result.generation_elapsed_seconds != null) && <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 border-t border-slate-100 pt-3 text-[10px] text-slate-400"><span>Retrieval {result.retrieval_elapsed_seconds == null ? '—' : elapsedLabel(result.retrieval_elapsed_seconds)}</span><span>Generation {result.generation_elapsed_seconds == null ? '—' : elapsedLabel(result.generation_elapsed_seconds)}</span>{result.retrieval_used != null && <span>{result.retrieval_used ? 'Evidence retrieval used' : 'No retrieval'}</span>}</div>}
      </div>
    </article>
  )
}

function HistoryItem({ run, active, onClick }: { run: ComparisonRun; active: boolean; onClick: () => void }) {
  const statuses = Object.values(run.systems).filter(Boolean).map((result) => result!.status)
  const failed = statuses.includes('failed')
  const abstained = statuses.includes('abstained')
  return (
    <button onClick={onClick} className={classNames('history-item w-full text-left', active && 'history-item-active')}>
      <div className="flex items-start justify-between gap-2"><span className="text-[11px] font-bold text-slate-800">{dateLabel(run.reference_date)}</span><span className={classNames('history-dot', failed ? 'bg-rose-400' : abstained ? 'bg-amber-400' : 'bg-emerald-400')} /></div>
      <p className="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-600">{run.question}</p>
      <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400"><span>{Object.keys(run.systems).length} system{Object.keys(run.systems).length === 1 ? '' : 's'}</span><span>{new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></div>
    </button>
  )
}

export default function App() {
  const [question, setQuestion] = useState(DEFAULT_QUESTION)
  const [referenceDate, setReferenceDate] = useState(DEFAULT_DATE)
  const [selectedSystems, setSelectedSystems] = useState<SystemId[]>(['A', 'B', 'C'])
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)
  const [comparison, setComparison] = useState<ComparisonRun | null>(null)
  const [history, setHistory] = useState<ComparisonRun[]>([])
  const [isComparing, setIsComparing] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [compareError, setCompareError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'compare' | 'history'>('compare')

  const refreshHealth = useCallback(async () => {
    try {
      const data = await api.health()
      setHealth(data)
      setHealthError(null)
    } catch (error) {
      setHealth(null)
      setHealthError(error instanceof Error ? error.message : 'Backend health check failed.')
    }
  }, [])

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const data = await api.history(30)
      setHistory(data.runs)
    } catch {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshHealth()
    void refreshHistory()
    const timer = window.setInterval(() => void refreshHealth(), 30000)
    return () => window.clearInterval(timer)
  }, [refreshHealth, refreshHistory])

  const toggleSystem = (system: SystemId) => {
    setSelectedSystems((current) => current.includes(system) ? current.filter((item) => item !== system) : [...current, system])
  }

  const handleCompare = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!question.trim() || !referenceDate || selectedSystems.length === 0 || isComparing) return
    setIsComparing(true)
    setCompareError(null)
    setActiveTab('compare')
    try {
      const result = await api.compare({ question, reference_date: referenceDate, systems: selectedSystems })
      setComparison(result)
      await refreshHistory()
      window.setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    } catch (error) {
      setCompareError(error instanceof Error ? error.message : 'Comparison request failed.')
    } finally {
      setIsComparing(false)
    }
  }

  const downloadComparison = () => {
    if (!comparison) return
    const content = JSON.stringify(comparison, null, 2)
    const url = URL.createObjectURL(new Blob([content], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `temporal-legal-qa-${comparison.comparison_id.slice(0, 8)}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const showRun = (run: ComparisonRun) => {
    setComparison(run)
    setQuestion(run.question)
    setReferenceDate(run.reference_date)
    setSelectedSystems(Object.keys(run.systems) as SystemId[])
    setActiveTab('compare')
    window.setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
  }

  const apiStatus = healthError ? 'offline' : health?.all_systems_available ? 'connected' : health ? 'degraded' : 'checking'

  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-800">
      <div className="soft-grid pointer-events-none fixed inset-x-0 top-0 h-[390px] opacity-60" />
      <header className="relative border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-4 px-4 py-3.5 sm:px-7 lg:px-10">
          <a href="#top" className="flex items-center gap-3 no-underline">
            <div className="flex h-10 w-10 items-center justify-center rounded-[13px] bg-[#17294b] text-white shadow-[0_5px_14px_rgba(23,41,75,.22)]"><Scale size={20} strokeWidth={1.8} /></div>
            <div><p className="display-font text-[14px] font-extrabold tracking-[-.035em] text-slate-900">Temporal Legal QA</p><p className="mt-0.5 hidden text-[10px] font-semibold uppercase tracking-[.12em] text-slate-400 sm:block">Research workspace</p></div>
          </a>
          <nav className="hidden items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1 md:flex">
            <button onClick={() => setActiveTab('compare')} className={classNames('nav-tab', activeTab === 'compare' && 'nav-tab-active')}><PanelTop size={14} /> Compare</button>
            <button onClick={() => { setActiveTab('history'); document.getElementById('history-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }} className={classNames('nav-tab', activeTab === 'history' && 'nav-tab-active')}><History size={14} /> History</button>
          </nav>
          <div className="flex items-center gap-2">
            <div className={classNames('backend-pill', apiStatus === 'connected' ? 'backend-connected' : apiStatus === 'degraded' ? 'backend-degraded' : apiStatus === 'offline' ? 'backend-offline' : 'backend-checking')}>
              {apiStatus === 'offline' ? <WifiOff size={14} /> : apiStatus === 'checking' ? <LoaderCircle className="animate-spin" size={14} /> : <Wifi size={14} />}
              <span className="hidden sm:inline">{apiStatus === 'connected' ? 'Backend connected' : apiStatus === 'degraded' ? 'Systems degraded' : apiStatus === 'offline' ? 'Backend offline' : 'Connecting'}</span>
              <span className="sm:hidden">{apiStatus === 'connected' ? 'Online' : apiStatus === 'degraded' ? 'Degraded' : apiStatus === 'offline' ? 'Offline' : '…'}</span>
            </div>
            <button className="icon-button hidden sm:flex" aria-label="Refresh backend status" onClick={() => void refreshHealth()}><Activity size={16} /></button>
          </div>
        </div>
      </header>

      <main id="top" className="relative mx-auto max-w-[1440px] px-4 pb-16 pt-7 sm:px-7 sm:pt-10 lg:px-10">
        <section className="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50/90 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[.13em] text-indigo-700"><Landmark size={13} /> Indian constitutional law</div>
            <h1 className="display-font text-[clamp(2rem,4.5vw,3.55rem)] font-extrabold leading-[1.08] tracking-[-.055em] text-[#17294a]">Temporal Legal QA</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-[15px]">Comparing Base LLM, Static RAG and Temporal RAG for Indian Constitutional Law.</p>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-slate-200/80 bg-white/80 px-3 py-2.5 text-xs text-slate-500 shadow-sm"><ShieldCheck size={15} className="text-indigo-600" /><span>Research systems · source-grounded comparison</span></div>
        </section>

        {healthError && <div role="alert" className="mb-6 flex items-center gap-3 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-sm text-rose-800"><WifiOff size={17} /><div className="flex-1"><span className="font-bold">Backend connection failed.</span> {healthError}</div><button onClick={() => void refreshHealth()} className="rounded-lg border border-rose-200 px-3 py-1.5 text-xs font-bold hover:bg-white">Retry</button></div>}
        {health?.status === 'degraded' && <div className="mb-6 flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-3.5 text-[13px] leading-5 text-amber-900"><TriangleAlert className="mt-0.5 shrink-0" size={16} /><p><span className="font-bold">Some systems are unavailable.</span> The backend reports prerequisites missing for one or more systems. Requests you select will still return explicit errors or abstentions; no substitute answer will be shown.</p></div>}

        <section aria-label="Experimental systems" className="mb-9 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {SYSTEMS.map((system) => <SystemOverviewCard key={system.id} system={system} available={health?.systems_available?.[system.id]} />)}
        </section>

        <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_318px]">
          <div className="min-w-0 space-y-7">
            <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_7px_24px_rgba(21,37,66,.045)] sm:p-6">
              <div className="mb-5 flex items-start justify-between gap-4">
                <div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.13em] text-indigo-700"><MessageSquareText size={14} /> Question workspace</div><h2 className="display-font mt-2 text-xl font-extrabold tracking-[-.035em] text-slate-900">Set up a comparison</h2><p className="mt-1 text-xs leading-5 text-slate-500">The same question and reference date are passed unchanged to each selected system.</p></div>
                <span className="hidden rounded-lg bg-slate-50 px-2.5 py-1.5 font-mono text-[10px] text-slate-400 sm:block">POST /api/compare</span>
              </div>
              <form onSubmit={handleCompare}>
                <label htmlFor="question" className="mb-2 block text-xs font-bold text-slate-700">Legal question</label>
                <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={4} maxLength={10000} required placeholder="Ask a question about the Constitution of India…" className="question-input w-full resize-y rounded-xl border border-slate-200 bg-[#fbfcfe] px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-indigo-300 focus:bg-white focus:ring-4 focus:ring-indigo-100" />
                <div className="mt-4 grid gap-5 sm:grid-cols-[220px_minmax(0,1fr)] sm:items-start">
                  <div>
                    <label htmlFor="reference-date" className="mb-2 flex items-center gap-1.5 text-xs font-bold text-slate-700"><CalendarDays size={14} className="text-slate-400" /> Reference date</label>
                    <input id="reference-date" type="date" value={referenceDate} onChange={(event) => setReferenceDate(event.target.value)} required className="date-input w-full rounded-xl border border-slate-200 bg-[#fbfcfe] px-3.5 py-3 text-sm font-semibold text-slate-700 outline-none focus:border-indigo-300 focus:ring-4 focus:ring-indigo-100" />
                    <p className="mt-2 text-[10px] leading-4 text-slate-400">Used for the question; only System C filters by temporal version.</p>
                  </div>
                  <fieldset>
                    <legend className="mb-2 text-xs font-bold text-slate-700">Systems to compare</legend>
                    <div className="grid gap-2 sm:grid-cols-3">
                      {SYSTEMS.map((system) => {
                        const selected = selectedSystems.includes(system.id)
                        const Icon = system.icon
                        return <button type="button" key={system.id} aria-pressed={selected} onClick={() => toggleSystem(system.id)} className={classNames('system-select', selected && 'system-select-active')}>
                          <span className={classNames('flex h-7 w-7 items-center justify-center rounded-lg', selected ? `tone-${system.tone}` : 'bg-slate-100 text-slate-400')}><Icon size={14} /></span><span className="min-w-0 flex-1 text-left"><span className="block text-[11px] font-bold">{system.name}</span><span className="block truncate text-[10px] text-slate-400">{system.shortName}</span></span><span className={classNames('check-box', selected && 'check-box-active')}>{selected && <Check size={11} />}</span>
                        </button>
                      })}
                    </div>
                  </fieldset>
                </div>
                {compareError && <div role="alert" className="mt-4 flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2.5 text-xs leading-5 text-rose-800"><CircleAlert size={15} className="mt-0.5 shrink-0" />{compareError}</div>}
                <div className="mt-5 flex flex-col-reverse gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-[11px] text-slate-400">No model answers are cached or fabricated in this interface.</p>
                  <button type="submit" disabled={isComparing || selectedSystems.length === 0 || !question.trim() || !referenceDate} className="primary-button inline-flex items-center justify-center gap-2 rounded-xl bg-[#243c68] px-5 py-3 text-sm font-bold text-white shadow-[0_5px_13px_rgba(36,60,104,.2)] transition hover:bg-[#1d3157] disabled:cursor-not-allowed disabled:opacity-55">
                    {isComparing ? <><LoaderCircle className="animate-spin" size={16} /> Running selected systems…</> : <><Scale size={16} /> Compare systems <ArrowRight size={15} /></>}
                  </button>
                </div>
              </form>
            </section>

            <section id="results" className="scroll-mt-6">
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.13em] text-indigo-700"><Activity size={14} /> Results comparison</div><h2 className="display-font mt-1.5 text-xl font-extrabold tracking-[-.035em] text-slate-900">System outputs</h2></div>
                {comparison && <div className="flex items-center gap-2"><span className="hidden text-[10px] text-slate-400 sm:inline">{dateLabel(comparison.reference_date)} · {comparison.comparison_id.slice(0, 8)}</span><button onClick={downloadComparison} className="secondary-button inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-700 hover:border-slate-300 hover:bg-slate-50"><Download size={14} /> Export JSON</button></div>}
              </div>
              {!comparison && !isComparing && <div className="empty-state rounded-2xl border border-dashed border-slate-300 bg-white/65 px-6 py-12 text-center"><span className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-700"><BookOpen size={21} /></span><h3 className="display-font mt-4 text-sm font-extrabold text-slate-800">Results will appear here</h3><p className="mx-auto mt-1.5 max-w-sm text-xs leading-5 text-slate-500">Submit a legal question to see the real output, evidence, timing and temporal selection returned by each system.</p><button onClick={() => document.getElementById('question')?.focus()} className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-indigo-700 hover:text-indigo-900">Write a question <ArrowDown size={13} /></button></div>}
              {isComparing && <div className="grid gap-4 lg:grid-cols-2"><div className="skeleton-card" /><div className="skeleton-card" /><div className="skeleton-card lg:col-span-2" /></div>}
              {comparison && !isComparing && <div className={classNames('grid gap-4', Object.keys(comparison.systems).length === 3 ? 'lg:grid-cols-2 2xl:grid-cols-3' : 'lg:grid-cols-2')}>
                {SYSTEMS.filter((system) => comparison.systems[system.id]).map((system) => <ResultCard key={system.id} system={system} result={comparison.systems[system.id]!} />)}
              </div>}
            </section>
          </div>

          <aside id="history-panel" className="scroll-mt-6 xl:sticky xl:top-5">
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_5px_20px_rgba(21,37,66,.04)]">
              <div className="flex items-center justify-between border-b border-slate-100 px-4 py-4">
                <div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.11em] text-slate-500"><History size={14} /> Run history</div><p className="mt-1 text-[11px] text-slate-400">Saved locally by the backend</p></div>
                <span className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-bold tabular-nums text-slate-600">{history.length}</span>
              </div>
              <div className="max-h-[430px] divide-y divide-slate-100 overflow-y-auto scrollbar-subtle">
                {historyLoading ? <div className="flex items-center justify-center gap-2 px-4 py-8 text-xs text-slate-400"><LoaderCircle size={14} className="animate-spin" />Loading saved runs…</div> : history.length === 0 ? <div className="px-4 py-8 text-center"><History size={19} className="mx-auto text-slate-300" /><p className="mt-2 text-xs font-semibold text-slate-600">No saved comparisons yet</p><p className="mt-1 text-[11px] text-slate-400">Completed and failed comparison records appear here.</p></div> : history.map((run) => <HistoryItem key={run.comparison_id} run={run} active={comparison?.comparison_id === run.comparison_id} onClick={() => showRun(run)} />)}
              </div>
              <div className="border-t border-slate-100 bg-slate-50/70 px-4 py-3"><p className="text-[10px] leading-4 text-slate-500">History preserves each system’s status. Failed requests and temporal abstentions remain distinct.</p></div>
            </section>
            <div className="mt-4 rounded-xl border border-slate-200/80 bg-white/70 p-4">
              <div className="flex items-center gap-2 text-[11px] font-bold text-slate-700"><ShieldCheck size={14} className="text-indigo-600" /> Research conditions</div>
              <ul className="mt-2 space-y-1.5 text-[10px] leading-4 text-slate-500"><li>• A answers without retrieval.</li><li>• B searches a fixed corpus without date filtering.</li><li>• C selects verified versions before retrieval.</li><li>• No accuracy score is inferred by this interface.</li></ul>
            </div>
          </aside>
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white/70">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-2 px-4 py-5 text-[10px] text-slate-400 sm:flex-row sm:items-center sm:justify-between sm:px-7 lg:px-10"><span>Temporal Legal QA · Research demonstration interface</span><span className="inline-flex items-center gap-1.5"><Command size={11} /> Outputs are experimental and should be checked against cited sources.</span></div>
      </footer>
    </div>
  )
}
