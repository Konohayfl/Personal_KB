// Shared by knowledge libraries and document collections; never mutate API data.
export function dateValue(value) {
  if (!value) return 0
  const result = new Date(String(value).replace(' ', 'T')).getTime()
  return Number.isFinite(result) ? result : 0
}

export function selectLibraries(items, query = '', sort = 'newest', titleKey = 'title') {
  const needle = query.trim().toLocaleLowerCase()
  return items.filter(item => String(item[titleKey] ?? '').toLocaleLowerCase().includes(needle))
    .sort((a, b) => {
      if (sort === 'name') return String(a[titleKey] ?? '').localeCompare(String(b[titleKey] ?? ''), 'zh-CN', { numeric: true })
      return (dateValue(b.crtTm) - dateValue(a.crtTm)) * (sort === 'oldest' ? -1 : 1)
    })
}

export function createdLabel(value) {
  const stamp = dateValue(value)
  if (!stamp) return '创建时间未记录'
  return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(stamp)) + ' 创建'
}

export function libraryTone(id) {
  return [...String(id ?? '')].reduce((sum, char) => sum + char.codePointAt(0), 0) % 6
}
