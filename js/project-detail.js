const detailRoot = document.getElementById('project-detail');
const imageViewer = document.getElementById('image-viewer');
const viewerImage = imageViewer.querySelector('img');

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function createSection(title, content) {
  const section = el('section', 'detail-section');
  section.append(el('h2', '', title), content);
  return section;
}

function appendTextSection(parent, title, value) {
  if (value?.trim()) parent.append(createSection(title, el('p', '', value)));
}

function detailHead(project) {
  const header = el('header', 'detail-head');
  const breadcrumb = el('div', 'breadcrumb');
  const back = el('a', '', '← 返回作品總覽');
  back.href = 'projects.html';
  breadcrumb.append(back);
  header.append(breadcrumb, el('h1', '', project.title));

  const meta = el('dl', 'detail-meta');
  const fields = [
    ['專案類型', project.projectType],
    ['技術分類', project.category],
    ['作業週次', formatCourseWeek(project.courseWeek)],
    ['作品日期', project.projectDate],
    ['狀態', project.status && createStatus(project.status)]
  ];
  for (const [label, value] of fields) {
    if (!value) continue;

    const entry = el('div');
    const definition = el('dd');
    if (label === '作品日期') {
      const date = el('time', '', value);
      date.dateTime = value;
      definition.append(date);
    } else {
      definition.append(value);
    }
    entry.append(el('dt', '', label), definition);
    meta.append(entry);
  }
  if (meta.children.length) header.append(meta);
  if (project.summary?.trim()) header.append(el('p', '', project.summary));
  return header;
}

function hasMedia(media) {
  return typeof media?.src === 'string' && Boolean(media.src.trim()) &&
    typeof media.alt === 'string' && Boolean(media.alt.trim());
}

function imageFigure(media, { className = 'detail-figure', zoom = false, caption, onError } = {}) {
  const figure = el('figure', className);
  const image = el('img');
  image.alt = media.alt;
  image.addEventListener('error', () => {
    figure.remove();
    onError?.();
  }, { once: true });

  if (zoom) {
    const trigger = el('button', 'image-preview');
    trigger.type = 'button';
    trigger.setAttribute('aria-label', '放大查看：' + media.alt);
    trigger.append(image, el('span', 'image-zoom', '放大查看'));
    trigger.addEventListener('click', () => {
      viewerImage.src = image.src;
      viewerImage.alt = image.alt;
      imageViewer.showModal();
    });
    figure.append(trigger);
  } else {
    figure.append(image);
  }

  if (caption) figure.append(el('figcaption', 'image-notice', caption));
  image.src = media.src;
  return figure;
}

function appendGallery(parent, screenshots) {
  if (!Array.isArray(screenshots)) return;

  const gallery = el('div', 'detail-gallery');
  const section = createSection('成果截圖', gallery);
  for (const media of screenshots) {
    if (!hasMedia(media)) continue;
    gallery.append(imageFigure(media, {
      zoom: true,
      onError: () => {
        if (!gallery.children.length) section.remove();
      }
    }));
  }
  if (gallery.children.length) parent.append(section);
}

function relatedLinks(project) {
  const items = [
    { label: 'GitHub 原始碼', url: project.githubUrl },
    { label: '線上展示', url: project.demoUrl },
    ...(Array.isArray(project.links) ? project.links : [])
  ];

  const links = el('ul', 'detail-links');
  const seen = new Set();
  for (const item of items) {
    if (typeof item?.label !== 'string' || !item.label.trim() || !/^https:\/\//i.test(item.url || '')) continue;
    let url;
    try {
      url = new URL(item.url);
    } catch {
      continue;
    }
    if (url.username || url.password || seen.has(url.href)) continue;
    seen.add(url.href);

    const link = el('a', 'btn btn-secondary', item.label);
    link.href = url.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    const listItem = el('li');
    listItem.append(link);
    links.append(listItem);
  }
  if (links.children.length) return createSection('相關連結', links);
  return null;
}

function renderDetail(project) {
  document.title = project.title + ' | My Project Hub 2.0';
  detailRoot.replaceChildren(detailHead(project));

  const cover = { src: project.image, alt: project.imageAlt || project.title };
  if (hasMedia(cover)) {
    detailRoot.append(imageFigure(cover, {
      className: 'detail-cover',
      zoom: project.imageType === 'screenshot',
      caption: project.imageType && project.imageType !== 'screenshot'
        ? '展示封面為佔位圖，取得實際操作截圖後可替換。'
        : undefined
    }));
  }

  const content = el('div', 'detail-content');
  appendTextSection(content, '專案動機', project.motivation);
  appendTextSection(content, '專案介紹', project.description);

  const features = (project.features || []).filter(item => item?.trim());
  if (features.length) {
    const list = el('ul', 'feature-list');
    list.append(...features.map(feature => el('li', '', feature)));
    content.append(createSection('核心功能', list));
  }

  if (hasMedia(project.systemDiagram)) {
    const section = createSection('系統流程圖', imageFigure(project.systemDiagram, {
      onError: () => section.remove()
    }));
    content.append(section);
  }

  appendTextSection(content, '開發成果', project.results);
  appendGallery(content, project.screenshots);

  const technologies = (project.technologies || []).filter(item => item?.trim());
  if (technologies.length) content.append(createSection('使用技術', createTags(technologies)));

  const reflection = project.lessonsLearned?.trim();
  if (reflection && !reflection.startsWith('待補充')) {
    appendTextSection(content, '學習與反思', reflection);
  }

  const links = relatedLinks(project);
  if (links) content.append(links);
  if (content.children.length) detailRoot.append(content);
}

function showDetailError(message) {
  const state = el('div', 'empty-state');
  const link = el('a', 'btn btn-secondary', '返回作品總覽');
  link.href = 'projects.html';
  state.append(el('p', '', message), link);
  detailRoot.replaceChildren(state);
}

async function initDetail() {
  const id = new URLSearchParams(location.search).get('id');
  if (!id) {
    showDetailError('未指定作品。請從作品列表選擇作品。');
    return;
  }

  let projects;
  try {
    projects = await loadProjects();
  } catch {
    showDetailError('資料載入失敗。請透過本機伺服器或 GitHub Pages 開啟網站。');
    return;
  }

  const project = projects.find(item => item.id === id);
  if (project) {
    renderDetail(project);
  } else {
    showDetailError('找不到這個作品，可能是連結錯誤或作品已移動。');
  }
}

initDetail();
