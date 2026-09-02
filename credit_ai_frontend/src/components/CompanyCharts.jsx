import { useEffect, useMemo, useState } from 'react'
import { BarChart3, Loader2, X } from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { fetchCompanyDetails } from '@/api/companyDetails'
import { extractChartData, formatCrore } from '@/lib/chartData'

const COLORS = ['#60a5fa', '#34d399', '#fbbf24', '#a78bfa', '#f87171', '#22d3ee', '#c084fc', '#fb7185']

const TICK = {
  fill: 'hsl(var(--muted-foreground))',
  fontSize: 11,
  fontFamily: 'Inter, system-ui, sans-serif',
}

function ChartLegend({ payload }) {
  if (!payload?.length) return null
  return (
    <div className="mt-3 flex flex-wrap justify-center gap-1.5">
      {payload.map((item) => (
        <span
          key={item.value}
          className="inline-flex items-center gap-1.5 rounded-full border border-border/50 bg-muted/50 px-2.5 py-0.5 text-[10px] font-medium text-foreground/80"
        >
          <span className="h-2 w-2 rounded-full" style={{ background: item.color }} />
          {item.value}
        </span>
      ))}
    </div>
  )
}

function PrettyTooltip({ active, payload, label, crores, suffix }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border border-border/70 bg-card/95 px-3 py-2 text-xs shadow-xl backdrop-blur-md">
      <p className="mb-1.5 font-semibold text-foreground">{label}</p>
      {payload.map((item) => (
        <p key={item.dataKey} className="flex items-center justify-between gap-4 py-0.5">
          <span className="inline-flex items-center gap-1.5 text-muted-foreground">
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: item.color }} />
            {item.name}
          </span>
          <span className="font-medium tabular-nums text-foreground">
            {crores ? formatCrore(item.value) : `${item.value ?? '—'}${suffix ?? ''}`}
          </span>
        </p>
      ))}
    </div>
  )
}

function ChartCard({ title, description, children, empty }) {
  return (
    <Card className="overflow-hidden border-border/60 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold tracking-tight">{title}</CardTitle>
        {description && <CardDescription className="text-[11px]">{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {empty ? (
          <p className="py-10 text-center text-xs text-muted-foreground">No data for this chart</p>
        ) : (
          <div className="h-72">{children}</div>
        )}
      </CardContent>
    </Card>
  )
}

const axis = {
  tick: TICK,
  tickLine: false,
  axisLine: { stroke: 'hsl(var(--border))' },
}

export function CompanyCharts({ companies, open, onClose }) {
  const [cin, setCin] = useState(companies[0]?.cin ?? '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [charts, setCharts] = useState(null)

  useEffect(() => {
    if (!open) return
    if (!cin && companies[0]?.cin) setCin(companies[0].cin)
  }, [open, companies, cin])

  useEffect(() => {
    if (!open || !cin) return
    const controller = new AbortController()
    setLoading(true)
    setError(null)
    fetchCompanyDetails(cin, controller.signal)
      .then((payload) => setCharts(extractChartData(payload)))
      .catch((err) => {
        if (err.name === 'AbortError') return
        setError(err.message)
        setCharts(null)
      })
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [open, cin])

  const selectedName = useMemo(
    () => companies.find((c) => c.cin === cin)?.legalName ?? charts?.companyName,
    [companies, cin, charts]
  )

  if (!open) return null

  return (
    <div className="absolute inset-0 z-20 flex flex-col bg-background/95 backdrop-blur-sm">
      <header className="flex h-12 shrink-0 items-center justify-between border-b px-4">
        <div className="flex min-w-0 items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">Charts</p>
            <p className="truncate text-[10px] text-muted-foreground">{selectedName}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {companies.length > 1 && (
            <select
              className="h-8 max-w-[220px] rounded-md border bg-background px-2 text-xs"
              value={cin}
              onChange={(event) => setCin(event.target.value)}
            >
              {companies.map((company) => (
                <option key={company.cin} value={company.cin}>
                  {company.legalName}
                </option>
              ))}
            </select>
          )}
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {loading && (
        <div className="flex flex-1 flex-col items-center justify-center gap-3">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading charts for {selectedName}…</p>
        </div>
      )}

      {!loading && error && (
        <div className="flex flex-1 items-center justify-center px-6">
          <p className="max-w-md text-center text-sm text-destructive">{error}</p>
        </div>
      )}

      {!loading && !error && charts && (
        <Tabs defaultValue="financials" className="flex min-h-0 flex-1 flex-col">
          <div className="shrink-0 border-b px-4 py-2">
            <TabsList>
              <TabsTrigger value="financials">Financials</TabsTrigger>
              <TabsTrigger value="credit">Credit</TabsTrigger>
              <TabsTrigger value="peers">Peers</TabsTrigger>
              <TabsTrigger value="other">Other</TabsTrigger>
            </TabsList>
          </div>
          <ScrollArea className="min-h-0 flex-1">
            <TabsContent value="financials" className="p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <ChartCard title="Revenue and profit" description="Standalone, ₹ crore" empty={!charts.pnl.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={charts.pnl}>
                      <defs>
                        <linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={COLORS[0]} stopOpacity={0.35} />
                          <stop offset="100%" stopColor={COLORS[0]} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} tickFormatter={(v) => v} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Legend content={<ChartLegend />} />
                      <Area type="monotone" dataKey="revenue" name="Revenue" stroke={COLORS[0]} fill="url(#revFill)" strokeWidth={2.4} />
                      <Line type="monotone" dataKey="operatingProfit" name="Operating profit" stroke={COLORS[1]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="pat" name="PAT" stroke={COLORS[2]} strokeWidth={2.2} dot={{ r: 3 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Year-on-year growth" description="%" empty={!charts.growth.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.growth}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip suffix="%" />} />
                      <Legend content={<ChartLegend />} />
                      <Bar dataKey="revenue" name="Revenue" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="operatingProfit" name="Op. profit" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="pat" name="PAT" fill={COLORS[2]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Margins and returns" description="%" empty={!charts.ratios.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={charts.ratios}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip suffix="%" />} />
                      <Legend content={<ChartLegend />} />
                      <Line type="monotone" dataKey="ebitdaMargin" name="EBITDA margin" stroke={COLORS[0]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="netMargin" name="Net margin" stroke={COLORS[1]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="roe" name="ROE" stroke={COLORS[3]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="roce" name="ROCE" stroke={COLORS[4]} strokeWidth={2.2} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Leverage" description="Debt/equity and interest cover" empty={!charts.leverage.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={charts.leverage}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} yAxisId="left" />
                      <YAxis {...axis} yAxisId="right" orientation="right" />
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                      <Bar yAxisId="left" dataKey="debtEquity" name="Debt / equity" fill={COLORS[4]} radius={[4, 4, 0, 0]} />
                      <Line yAxisId="right" type="monotone" dataKey="interestCover" name="Interest cover" stroke={COLORS[1]} strokeWidth={2.4} dot={{ r: 3 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Equity vs debt" description="₹ crore" empty={!charts.balanceSheet.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.balanceSheet}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Legend content={<ChartLegend />} />
                      <Bar dataKey="equity" name="Equity" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="debt" name="Debt" fill={COLORS[4]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Liquidity" description="Current vs quick ratio" empty={!charts.liquidity.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={charts.liquidity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                      <Line type="monotone" dataKey="currentRatio" name="Current ratio" stroke={COLORS[0]} strokeWidth={2.3} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="quickRatio" name="Quick ratio" stroke={COLORS[5]} strokeWidth={2.3} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Working capital stock" description="₹ crore" empty={!charts.liquidity.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.liquidity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Legend content={<ChartLegend />} />
                      <Bar dataKey="currentAssets" name="Current assets" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="currentLiabilities" name="Current liabilities" fill={COLORS[2]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Cash flow" description="₹ crore" empty={!charts.cashFlow.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.cashFlow}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Legend content={<ChartLegend />} />
                      <Bar dataKey="operating" name="Operating" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="investing" name="Investing" fill={COLORS[2]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="financing" name="Financing" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </TabsContent>
            <TabsContent value="credit" className="p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <ChartCard title="Probe financial scores" description="1–5 scale" empty={!charts.probeScores.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.probeScores} layout="vertical" margin={{ left: 24 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis type="number" domain={[0, 5]} {...axis} />
                      <YAxis type="category" dataKey="name" width={96} {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Bar dataKey="value" name="Score" radius={[0, 6, 6, 0]}>
                        {charts.probeScores.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Working capital days" empty={!charts.workingCapital.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={charts.workingCapital}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="year" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                      <Line type="monotone" dataKey="inventoryDays" name="Inventory" stroke={COLORS[0]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="debtorDays" name="Debtors" stroke={COLORS[2]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="payableDays" name="Payables" stroke={COLORS[1]} strokeWidth={2.2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="ccc" name="CCC" stroke={COLORS[4]} strokeWidth={2.2} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="MSME payment delays" description="₹ crore" empty={!charts.msmeTrend.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={charts.msmeTrend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="period" {...axis} interval={0} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Area type="monotone" dataKey="amount" name="Overdue" stroke={COLORS[4]} fill={COLORS[4]} fillOpacity={0.2} strokeWidth={2.2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Latest MSME suppliers due" description="₹ crore" empty={!charts.msmeSuppliers.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.msmeSuppliers} layout="vertical" margin={{ left: 16 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis type="number" {...axis} />
                      <YAxis type="category" dataKey="name" width={120} {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Bar dataKey="amount" name="Due" fill={COLORS[2]} radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </TabsContent>
            <TabsContent value="peers" className="p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <ChartCard title="Peer revenue" description="₹ crore" empty={!charts.peers.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.peers} layout="vertical" margin={{ left: 16 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis type="number" {...axis} />
                      <YAxis type="category" dataKey="name" width={140} {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Bar dataKey="revenue" name="Revenue" fill={COLORS[0]} radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Vs industry median" empty={!charts.peerBench.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.peerBench}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="metric" {...axis} />
                      <YAxis {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                      <Bar dataKey="company" name="Company" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                      <Bar dataKey="median" name="Median" fill={COLORS[5]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Related-party amounts" description="Latest year, ₹ crore" empty={!charts.relatedParties.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.relatedParties} layout="vertical" margin={{ left: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis type="number" {...axis} />
                      <YAxis type="category" dataKey="name" width={160} {...axis} />
                      <Tooltip content={<PrettyTooltip crores />} />
                      <Bar dataKey="amount" name="Amount" fill={COLORS[3]} radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Shareholders >5%" description="%" empty={!charts.shareholders.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={charts.shareholders} dataKey="value" nameKey="name" innerRadius={52} outerRadius={84} paddingAngle={2} stroke="transparent">
                        {charts.shareholders.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip content={<PrettyTooltip suffix="%" />} />
                      <Legend content={<ChartLegend />} />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </TabsContent>
            <TabsContent value="other" className="p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <ChartCard title="Legal cases by status" empty={!charts.legalByStatus.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.legalByStatus}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="name" {...axis} />
                      <YAxis allowDecimals={false} {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Bar dataKey="value" name="Cases" radius={[4, 4, 0, 0]}>
                        {charts.legalByStatus.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="Legal cases by severity" empty={!charts.legalBySeverity.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={charts.legalBySeverity} dataKey="value" nameKey="name" innerRadius={52} outerRadius={84} paddingAngle={2} stroke="transparent">
                        {charts.legalBySeverity.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="GST registrations by status" empty={!charts.gstByStatus.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={charts.gstByStatus} dataKey="value" nameKey="name" innerRadius={52} outerRadius={84} paddingAngle={2} stroke="transparent">
                        {charts.gstByStatus.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip content={<PrettyTooltip />} />
                      <Legend content={<ChartLegend />} />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="GST by state" empty={!charts.gstByState.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.gstByState} layout="vertical" margin={{ left: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis type="number" allowDecimals={false} {...axis} />
                      <YAxis type="category" dataKey="name" width={120} {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Bar dataKey="value" name="GSTINs" fill={COLORS[5]} radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
                <ChartCard title="GST filing timeliness" empty={!charts.gstTimeliness.length}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.gstTimeliness}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.7} />
                      <XAxis dataKey="name" {...axis} />
                      <YAxis allowDecimals={false} {...axis} />
                      <Tooltip content={<PrettyTooltip />} />
                      <Bar dataKey="value" name="Registrations" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </TabsContent>
          </ScrollArea>
        </Tabs>
      )}
    </div>
  )
}
