function aboutElement(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function aboutCard(title, ...content) {
  const card = aboutElement('article', undefined, 'about-card');
  card.append(aboutElement('h3', title), ...content);
  return card;
}

function publicProfileLink(link) {
  if (!link?.label || !/^https:\/\//i.test(link.url)) return null;

  let url;
  try {
    url = new URL(link.url);
  } catch {
    return null;
  }
  if (url.username || url.password) return null;

  const anchor = aboutElement('a', link.label, 'btn btn-secondary');
  anchor.href = url.href;
  anchor.target = '_blank';
  anchor.rel = 'noopener noreferrer';
  return anchor;
}

function isProfile(data) {
  return typeof data?.intro?.role === 'string' &&
    typeof data.intro.roleEn === 'string' &&
    typeof data.intro.description === 'string' &&
    Array.isArray(data.education) &&
    typeof data.skills?.note === 'string' &&
    Array.isArray(data.skills.groups) &&
    Array.isArray(data.interests) &&
    Array.isArray(data.links) &&
    Array.isArray(data.site?.paragraphs);
}

async function initAbout() {
  const intro = document.getElementById('profile-intro');

  try {
    const profile = await loadSiteData('data/profile.json', window.PROFILE_FALLBACK, isProfile);
    if (!profile) throw new Error('缺少個人資料備援');

    const roleEn = aboutElement('p', profile.intro.roleEn, 'about-role-en');
    roleEn.lang = 'en';

    document.getElementById('profile-education').replaceChildren(
      ...profile.education.map(item => aboutCard(item.school,
        aboutElement('p', item.program),
        aboutElement('p', item.degree, 'about-secondary')
      ))
    );

    document.getElementById('profile-skills-note').textContent = profile.skills.note;
    document.getElementById('profile-skills').replaceChildren(
      ...profile.skills.groups.map(group => {
        const tags = aboutElement('div', undefined, 'tags');
        tags.append(...group.technologies.map(technology => aboutElement('span', technology, 'tag')));
        return aboutCard(group.title, tags);
      })
    );

    document.getElementById('profile-interests').replaceChildren(
      ...profile.interests.map(item => aboutCard(item.title, aboutElement('p', item.description)))
    );
    document.getElementById('profile-site').replaceChildren(
      ...profile.site.paragraphs.map(text => aboutElement('p', text))
    );

    const links = profile.links.map(publicProfileLink).filter(Boolean);
    document.getElementById('profile-links').prepend(...links);
    intro.replaceChildren(
      aboutElement('p', profile.intro.role, 'about-role'),
      roleEn,
      aboutElement('p', profile.intro.description, 'about-intro')
    );
    document.getElementById('profile-content').hidden = false;
  } catch {
    intro.replaceChildren(aboutElement('p', '目前無法載入個人資料，請稍後重試。', 'about-secondary'));
  }
}

initAbout();
