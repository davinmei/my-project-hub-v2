const PROJECT_DATA_URL = 'data/projects.json';

function loadProjects() {
  return loadSiteData(PROJECT_DATA_URL, window.PROJECTS_FALLBACK, Array.isArray, []);
}

function getAddedOrder(project, index) {
  return project.addedOrder ?? index + 1;
}

function getProjectValues(projects, field) {
  return [...new Set(projects.map(project => project[field]).filter(Boolean))];
}

function formatCourseWeek(week) {
  return Number.isInteger(week) && week > 0 ? '第 ' + week + ' 週' : '';
}

function createStatus(status) {
  const badge = document.createElement('span');
  badge.className = 'status' + (status === 'in-progress' ? ' progress' : '');
  badge.textContent = status === 'completed' ? '已完成' : '開發中';
  return badge;
}

function createTags(technologies) {
  const tags = document.createElement('div');
  tags.className = 'tags';
  for (const technology of technologies) {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = technology;
    tags.append(tag);
  }
  return tags;
}

function createCard(project, { showProjectInfo = false } = {}) {
  const article = document.createElement('article');
  article.className = 'project-card';
  const href = 'project.html?id=' + encodeURIComponent(project.id);

  const cover = document.createElement('a');
  cover.className = 'card-media';
  cover.href = href;
  cover.setAttribute('aria-label', '查看' + project.title + '詳細介紹');
  const image = document.createElement('img');
  image.src = project.image;
  image.alt = project.imageAlt || project.title;
  image.loading = 'lazy';
  cover.append(image);

  const body = document.createElement('div');
  body.className = 'card-body';
  const meta = document.createElement('div');
  meta.className = 'card-meta';

  const category = document.createElement('span');
  category.className = 'pill';
  category.textContent = project.category;
  meta.append(category, createStatus(project.status));

  if (showProjectInfo) {
    const info = [project.projectType, formatCourseWeek(project.courseWeek)].filter(Boolean);
    if (info.length) {
      const label = document.createElement('div');
      label.className = 'card-project-info';
      label.textContent = info.join(' · ');
      meta.append(label);
    }
  }

  const title = document.createElement('h3');
  title.textContent = project.title;
  const summary = document.createElement('p');
  summary.textContent = project.summary;

  const tags = createTags((project.technologies || []).slice(0, 4));
  const action = document.createElement('a');
  action.className = 'btn btn-secondary card-action';
  action.href = href;
  action.textContent = '查看作品';
  action.setAttribute('aria-label', '查看作品：' + project.title);

  body.append(meta, title, summary, tags, action);
  article.append(cover, body);
  return article;
}

function showError(target, message) {
  const state = document.createElement('div');
  state.className = 'empty-state';
  state.textContent = message;
  target.replaceChildren(state);
}

async function initList() {
  const target = document.getElementById('all-projects');
  if (!target) return;

  const form = document.getElementById('project-filters');
  const search = document.getElementById('project-search');
  const type = document.getElementById('type-filter');
  const category = document.getElementById('category-filter');
  const sort = document.getElementById('project-sort');
  const clear = document.getElementById('clear-filters');
  const count = document.getElementById('results-count');
  form.addEventListener('submit', event => event.preventDefault());

  let projects;
  try {
    projects = await loadProjects();
  } catch {
    count.textContent = '無法讀取作品數量';
    showError(target, '無法載入作品資料，請稍後重試。');
    return;
  }

  for (const value of getProjectValues(projects, 'category')) {
    category.add(new Option(value, value));
  }

  const entries = projects.map((project, index) => ({
    project,
    index,
    order: getAddedOrder(project, index),
    searchable: [
      project.title, project.summary, project.description, project.category,
      project.projectType, ...(project.technologies || [])
    ].join(' ').toLocaleLowerCase('zh-Hant')
  }));
  const titles = new Intl.Collator('zh-Hant', { numeric: true, sensitivity: 'base' });
  const byAddedOrder = (a, b) => a.order - b.order || a.index - b.index;
  const comparisons = {
    newest: (a, b) => byAddedOrder(b, a),
    oldest: byAddedOrder,
    title: (a, b) => titles.compare(a.project.title, b.project.title) || a.index - b.index
  };

  function render() {
    const query = search.value.trim().toLocaleLowerCase('zh-Hant');
    const filtered = entries.filter(({ project, searchable }) =>
      (!type.value || project.projectType === type.value) &&
      (!category.value || project.category === category.value) &&
      searchable.includes(query)
    );
    filtered.sort(comparisons[sort.value]);
    count.textContent = '共找到 ' + filtered.length + ' 個作品';

    if (filtered.length) {
      target.replaceChildren(...filtered.map(({ project }) => createCard(project, { showProjectInfo: true })));
    } else {
      const message = projects.length
        ? '沒有符合條件的作品，請試試其他關鍵字或清除條件。'
        : '目前沒有收錄作品。';
      showError(target, message);
    }
  }

  form.addEventListener('input', render);
  clear.addEventListener('click', () => {
    form.reset();
    render();
  });
  render();
}

initList();
