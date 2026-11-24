const toggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('.nav-links');

if (toggle && menu) {
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('open', open);
  });
}

async function initHomepage() {
  const featuredTarget = document.getElementById('featured-projects');
  if (!featuredTarget) return;

  const latestTarget = document.getElementById('latest-project');
  const stats = document.getElementById('project-stats');
  let projects;
  try {
    projects = await loadProjects();
  } catch {
    showError(stats, '目前無法載入作品統計。');
    showError(latestTarget, '目前無法載入最新作品。');
    showError(featuredTarget, '目前無法載入精選作品。');
    return;
  }

  const categories = [...new Set(projects.map(project => project.category))];
  document.getElementById('project-count').textContent = projects.length;
  document.getElementById('category-count').textContent = categories.length;
  document.getElementById('category-list').textContent = categories.join(' · ') || '尚無分類';

  const latest = projects.reduce((newest, project, index) => {
    const order = project.addedOrder ?? index + 1;
    return order >= newest.order ? { project, order } : newest;
  }, { order: 0 }).project;

  if (latest) {
    const card = createCard(latest);
    card.classList.add('project-card--latest');
    latestTarget.replaceChildren(card);
  } else {
    showError(latestTarget, '目前沒有作品。');
  }

  const featured = projects.filter(project => project.featured).slice(0, 2);
  if (featured.length) {
    featuredTarget.replaceChildren(...featured.map(createCard));
  } else {
    showError(featuredTarget, '目前沒有精選作品。');
  }
}

initHomepage();
initList();
