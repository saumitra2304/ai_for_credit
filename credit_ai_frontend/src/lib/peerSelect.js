export function suggestedPeers(charts, { excludeCins = [], limit = 3 } = {}) {
  const blocked = new Set(
    (excludeCins || []).map((cin) => String(cin || '').trim().toUpperCase()).filter(Boolean)
  )
  const ranked = [...(charts?.peers || [])]
    .filter((peer) => peer?.cin && peer.revenue != null && !blocked.has(String(peer.cin).toUpperCase()))
    .sort((a, b) => (b.revenue ?? 0) - (a.revenue ?? 0))

  const out = []
  const seen = new Set()
  for (const peer of ranked) {
    const cin = String(peer.cin).trim().toUpperCase()
    if (!cin || seen.has(cin)) continue
    seen.add(cin)
    out.push({
      cin,
      legalName: peer.legalName || peer.name || cin,
      name: peer.name || peer.legalName || cin,
      revenue: peer.revenue,
      source: 'probe',
    })
    if (out.length >= limit) break
  }
  return out
}

export function suggestedPeersFromCharts(chartSets, options) {
  return suggestedPeers(
    { peers: (chartSets || []).flatMap((charts) => charts?.peers || []) },
    options
  )
}

export function selectPeerCins(charts, options) {
  return suggestedPeers(charts, options).map((peer) => peer.cin)
}

export function extraCinsText(peers) {
  return (peers || [])
    .map((peer) => (typeof peer === 'string' ? peer : peer?.cin))
    .filter(Boolean)
    .join(', ')
}
