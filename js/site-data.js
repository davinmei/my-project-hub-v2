async function loadSiteData(url, fallback, isValid, fileDefault = null) {
  // HTTP 優先讀取 JSON，file:// 使用已載入的備援。
  if (location.protocol === 'file:') return isValid(fallback) ? fallback : fileDefault;

  try {
    const response = await fetch(url, { cache: 'no-cache' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    if (!isValid(data)) throw new Error('資料格式不正確');
    return data;
  } catch (error) {
    if (isValid(fallback)) return fallback;
    throw error;
  }
}
