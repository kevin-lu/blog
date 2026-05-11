export interface ArticleHeading {
  id: string;
  text: string;
  level: number;
}

const HTML_BLOCK_TAG_RE = /<\/?(?:article|section|div|p|br|hr|h[1-6]|ul|ol|li|blockquote|pre|code|table|thead|tbody|tr|th|td|img|a|strong|em|b|i|u|s|mark)\b/i;
const MARKDOWN_SIGNAL_RE = /(^|\n)\s{0,3}(#{1,6}\s+|```|~~~|[-*+]\s+|\d+[.)]\s+|>\s+|\|.+\|)/;

export function normalizeArticleContent(content?: string | null): string {
  return unwrapMarkdownFence(stripThinkingContent(content || '')).trim();
}

export function stripThinkingContent(content: string): string {
  return content
    .replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, '')
    .replace(/<thinking\b[^>]*>[\s\S]*?<\/thinking>/gi, '')
    .replace(/<reasoning\b[^>]*>[\s\S]*?<\/reasoning>/gi, '')
    .trim();
}

export function isHtmlContent(content: string): boolean {
  const normalized = content.trim();
  if (!normalized) return false;
  return HTML_BLOCK_TAG_RE.test(normalized) && !MARKDOWN_SIGNAL_RE.test(normalized);
}

export function renderArticleContent(content?: string | null): string {
  const normalized = normalizeArticleContent(content);
  if (!normalized) return '';

  if (isHtmlContent(normalized)) {
    return sanitizeHtml(normalized);
  }

  return markdownToHtml(normalized);
}

export function extractArticleHeadings(content?: string | null): ArticleHeading[] {
  const normalized = normalizeArticleContent(content);
  if (!normalized) return [];

  const headings: ArticleHeading[] = [];
  const seen = new Map<string, number>();

  if (isHtmlContent(normalized)) {
    const headingRe = /<h([2-3])\b[^>]*>([\s\S]*?)<\/h\1>/gi;
    let match: RegExpExecArray | null;
    while ((match = headingRe.exec(normalized))) {
      const text = decodeBasicEntities(stripHtml(match[2])).trim();
      if (!text) continue;
      headings.push({
        id: uniqueHeadingId(text, seen),
        text,
        level: Number(match[1]),
      });
    }
    return headings;
  }

  let inCode = false;
  for (const line of normalized.replace(/\r\n?/g, '\n').split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) {
      inCode = !inCode;
      continue;
    }
    if (inCode) continue;

    const match = /^(#{2,3})\s+(.+?)\s*#*\s*$/.exec(line.trim());
    if (!match) continue;

    const text = stripMarkdownInline(match[2]).trim();
    if (!text) continue;
    headings.push({
      id: uniqueHeadingId(text, seen),
      text,
      level: match[1].length,
    });
  }

  return headings;
}

export function markdownToHtml(markdown: string): string {
  const lines = normalizeArticleContent(markdown).replace(/\r\n?/g, '\n').split('\n');
  const html: string[] = [];
  const seenHeadings = new Map<string, number>();

  let paragraph: string[] = [];
  let listType: 'ul' | 'ol' | null = null;
  let listItems: string[] = [];
  let quoteLines: string[] = [];
  let codeFence: string | null = null;
  let codeLanguage = '';
  let codeLines: string[] = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    html.push(`<p>${renderInline(paragraph.join(' '))}</p>`);
    paragraph = [];
  };

  const flushList = () => {
    if (!listType || !listItems.length) return;
    html.push(`<${listType}>${listItems.join('')}</${listType}>`);
    listType = null;
    listItems = [];
  };

  const flushQuote = () => {
    if (!quoteLines.length) return;
    const quoteBody = quoteLines.map(line => renderInline(line)).join('<br>');
    html.push(`<blockquote>${quoteBody}</blockquote>`);
    quoteLines = [];
  };

  const flushCode = () => {
    if (!codeFence) return;
    const languageClass = codeLanguage ? ` class="language-${escapeAttribute(codeLanguage)}"` : '';
    html.push(`<pre><code${languageClass}>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
    codeFence = null;
    codeLanguage = '';
    codeLines = [];
  };

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trim();

    if (codeFence) {
      if (trimmed.startsWith(codeFence)) {
        flushCode();
      } else {
        codeLines.push(line);
      }
      continue;
    }

    const codeStart = /^(```|~~~)\s*([\w-]+)?\s*$/.exec(trimmed);
    if (codeStart) {
      flushParagraph();
      flushList();
      flushQuote();
      codeFence = codeStart[1];
      codeLanguage = codeStart[2] || '';
      continue;
    }

    if (!trimmed) {
      flushParagraph();
      flushList();
      flushQuote();
      continue;
    }

    if (isTableStart(lines, index)) {
      flushParagraph();
      flushList();
      flushQuote();
      const tableLines = [lines[index]];
      index += 2;
      while (index < lines.length && isTableRow(lines[index])) {
        tableLines.push(lines[index]);
        index += 1;
      }
      index -= 1;
      html.push(renderTable(tableLines));
      continue;
    }

    const heading = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(trimmed);
    if (heading) {
      flushParagraph();
      flushList();
      flushQuote();
      const level = heading[1].length;
      const text = heading[2].trim();
      const id = uniqueHeadingId(stripMarkdownInline(text), seenHeadings);
      html.push(`<h${level} id="${escapeAttribute(id)}">${renderInline(text)}</h${level}>`);
      continue;
    }

    if (/^([-*_])\1{2,}$/.test(trimmed)) {
      flushParagraph();
      flushList();
      flushQuote();
      html.push('<hr>');
      continue;
    }

    const quote = /^>\s?(.*)$/.exec(line);
    if (quote) {
      flushParagraph();
      flushList();
      quoteLines.push(quote[1].trim());
      continue;
    }

    const unordered = /^\s*[-*+]\s+(.+)$/.exec(line);
    const ordered = /^\s*\d+[.)]\s+(.+)$/.exec(line);
    if (unordered || ordered) {
      flushParagraph();
      flushQuote();
      const nextType = unordered ? 'ul' : 'ol';
      if (listType && listType !== nextType) {
        flushList();
      }
      listType = nextType;
      listItems.push(`<li>${renderInline((unordered || ordered)?.[1] || '')}</li>`);
      continue;
    }

    flushList();
    flushQuote();
    paragraph.push(trimmed);
  }

  flushCode();
  flushParagraph();
  flushList();
  flushQuote();

  return html.join('\n');
}

export function sanitizeHtml(html: string): string {
  return html
    .replace(/<\s*(script|style|iframe|object|embed|form|input|button|textarea|select|link|meta|base|svg|math)\b[\s\S]*?<\/\s*\1\s*>/gi, '')
    .replace(/<\s*\/?\s*(script|style|iframe|object|embed|form|input|button|textarea|select|link|meta|base|svg|math)\b[^>]*>/gi, '')
    .replace(/\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')
    .replace(/\s+(href|src)\s*=\s*(['"])\s*(?:javascript:|data:text\/html)[\s\S]*?\2/gi, '')
    .replace(/\s+(href|src)\s*=\s*(?:javascript:|data:text\/html)[^\s>]*/gi, '');
}

function unwrapMarkdownFence(content: string): string {
  return content.replace(/^\s*(?:```|~~~)(?:markdown|md)?\s*\n([\s\S]*?)\n(?:```|~~~)\s*$/i, '$1');
}

function renderInline(value: string): string {
  const tokens: string[] = [];
  const stashHtml = (html: string) => {
    tokens.push(html);
    return `\u0000${tokens.length - 1}\u0000`;
  };

  let text = value.replace(/`([^`]+)`/g, (_, code: string) => {
    return stashHtml(`<code>${escapeHtml(code)}</code>`);
  });

  text = escapeHtml(text);
  text = text.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;([^&]*)&quot;)?\)/g, (_, alt: string, url: string, title: string) => {
    const safeUrl = sanitizeUrl(url);
    if (!safeUrl) return escapeHtml(alt || '');
    const titleAttr = title ? ` title="${escapeAttribute(title)}"` : '';
    return stashHtml(`<img src="${escapeAttribute(safeUrl)}" alt="${escapeAttribute(alt || '')}"${titleAttr} loading="lazy">`);
  });
  text = text.replace(/\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;([^&]*)&quot;)?\)/g, (_, label: string, url: string, title: string) => {
    const safeUrl = sanitizeUrl(url);
    if (!safeUrl) return label;
    const titleAttr = title ? ` title="${escapeAttribute(title)}"` : '';
    return stashHtml(`<a href="${escapeAttribute(safeUrl)}"${titleAttr} target="_blank" rel="noopener noreferrer">${label}</a>`);
  });
  text = text
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/__([^_]+)__/g, '<strong>$1</strong>')
    .replace(/~~([^~]+)~~/g, '<del>$1</del>')
    .replace(/(^|[^\*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>')
    .replace(/(^|[^_])_([^_\n]+)_(?!_)/g, '$1<em>$2</em>');

  return text.replace(/\u0000(\d+)\u0000/g, (_, index: string) => tokens[Number(index)] || '');
}

function renderTable(rows: string[]): string {
  const [headerLine, ...bodyLines] = rows;
  const headers = splitTableRow(headerLine);
  const body = bodyLines.map(row => splitTableRow(row));

  const thead = `<thead><tr>${headers.map(cell => `<th>${renderInline(cell)}</th>`).join('')}</tr></thead>`;
  const tbody = `<tbody>${body.map(row => `<tr>${row.map(cell => `<td>${renderInline(cell)}</td>`).join('')}</tr>`).join('')}</tbody>`;
  return `<table>${thead}${tbody}</table>`;
}

function isTableStart(lines: string[], index: number): boolean {
  return isTableRow(lines[index]) && index + 1 < lines.length && isTableDivider(lines[index + 1]);
}

function isTableRow(line: string): boolean {
  return line.includes('|') && splitTableRow(line).length > 1;
}

function isTableDivider(line: string): boolean {
  const cells = splitTableRow(line);
  return cells.length > 1 && cells.every(cell => /^:?-{3,}:?$/.test(cell.trim()));
}

function splitTableRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map(cell => cell.trim());
}

function uniqueHeadingId(text: string, seen: Map<string, number>): string {
  const base = slugifyHeading(text) || 'section';
  const count = seen.get(base) || 0;
  seen.set(base, count + 1);
  return count === 0 ? base : `${base}-${count + 1}`;
}

function slugifyHeading(text: string): string {
  return stripMarkdownInline(text)
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function stripMarkdownInline(text: string): string {
  return text
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[`*_~#>]/g, '')
    .trim();
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, '');
}

function decodeBasicEntities(text: string): string {
  return text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function sanitizeUrl(url: string): string {
  const trimmed = decodeBasicEntities(url).trim();
  if (/^(https?:|mailto:|tel:|#|\/(?!\/)|\.\.?\/)/i.test(trimmed)) {
    return trimmed;
  }
  return '';
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeAttribute(value: string): string {
  return escapeHtml(value).replace(/`/g, '&#96;');
}
