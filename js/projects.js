const PROJECT_DATA_URL = 'data/projects.json';
async function loadProjects(){
  // HTTP / GitHub Pages 讀取 JSON；file:// 直接開啟時使用自動產生的備援資料。
  if(location.protocol === 'file:') return window.PROJECTS_FALLBACK || [];
  try {
    const response = await fetch(PROJECT_DATA_URL,{cache:'no-cache'});
    if (!response.ok) throw new Error('HTTP '+response.status);
    const data = await response.json();
    if (!Array.isArray(data)) throw new Error('作品資料格式不正確');
    return data;
  } catch (e) {
    if(Array.isArray(window.PROJECTS_FALLBACK)) return window.PROJECTS_FALLBACK;
    throw e;
  }
}

function createCard(project) {
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
  const status = document.createElement('span');
  status.className = 'status' + (project.status === 'in-progress' ? ' progress' : '');
  status.textContent = project.status === 'completed' ? '已完成' : '開發中';
  meta.append(category, status);

  const title = document.createElement('h3');
  title.textContent = project.title;
  const summary = document.createElement('p');
  summary.textContent = project.summary;

  const tags = document.createElement('div');
  tags.className = 'tags';
  for (const technology of (project.technologies || []).slice(0, 4)) {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = technology;
    tags.append(tag);
  }

  const action = document.createElement('a');
  action.className = 'btn btn-secondary card-action';
  action.href = href;
  action.textContent = '查看作品';
  action.setAttribute('aria-label', '查看作品：' + project.title);

  body.append(meta, title, summary, tags, action);
  article.append(cover, body);
  return article;
}

function showError(node,msg){node.replaceChildren();const x=document.createElement('div');x.className='empty-state';x.textContent=msg;node.append(x)}

async function initList(){
 const target=document.getElementById('all-projects');if(!target)return;
 const search=document.getElementById('project-search'),buttons=document.getElementById('category-filters'),count=document.getElementById('results-count');let all=[],category='全部作品';
 try{all=await loadProjects()}catch(e){showError(target,'無法載入作品資料。請確認 data/projects.json 存在，並透過網站伺服器開啟。');return}
 const categories=['全部作品',...new Set(all.map(p=>p.category))];
 function render(){const q=search.value.trim().toLocaleLowerCase('zh-Hant');const filtered=all.filter(p=>(category==='全部作品'||p.category===category)&&[p.title,p.category,p.summary,...(p.technologies||[])].join(' ').toLocaleLowerCase('zh-Hant').includes(q));count.textContent='共找到 '+filtered.length+' 個作品';if(filtered.length){target.replaceChildren(...filtered.map(createCard));}else{showError(target,'沒有符合條件的作品，試試其他關鍵字或分類。')}}
 categories.forEach(c=>{const b=document.createElement('button');b.type='button';b.className='filter-button'+(c===category?' active':'');b.textContent=c;b.setAttribute('aria-pressed',String(c===category));b.addEventListener('click',()=>{category=c;buttons.querySelectorAll('button').forEach(x=>{const selected=x===b;x.classList.toggle('active',selected);x.setAttribute('aria-pressed',String(selected))});render()});buttons.append(b)});
 search.addEventListener('input',render);render();
}
