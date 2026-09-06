const THEME_KEY = 'kuber-theme'

export function getTheme() {
  try {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    // Ignore.
  }
  return 'light'
}

export function applyTheme(theme) {
  const next = theme === 'dark' ? 'dark' : 'light'
  const root = document.documentElement
  root.classList.toggle('dark', next === 'dark')
  root.style.colorScheme = next
  try {
    localStorage.setItem(THEME_KEY, next)
  } catch {
    // Ignore.
  }
  return next
}
