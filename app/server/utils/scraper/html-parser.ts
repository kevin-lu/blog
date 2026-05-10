// app/server/utils/scraper/html-parser.ts

export interface ParsedContent {
  text: string;
  codeBlocks: Array<{
    language: string;
    code: string;
  }>;
  images: Array<{
    src: string;
    alt: string;
  }>;
  links: Array<{
    text: string;
    href: string;
  }>;
}

export function parseHtmlContent(html: string): ParsedContent {
  const text = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const codeBlocks: Array<{ language: string; code: string }> = [];
  const codeBlockRegex = /<pre[^>]*>([\s\S]*?)<\/pre>/gi;
  let match;
  while ((match = codeBlockRegex.exec(html)) !== null) {
    const codeContent = match[1]
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&');
    codeBlocks.push({
      language: 'javascript',
      code: codeContent,
    });
  }

  const images: Array<{ src: string; alt: string }> = [];
  const imageRegex = /<img[^>]+src="([^"]+)"[^>]*>/gi;
  let imageMatch;
  while ((imageMatch = imageRegex.exec(html)) !== null) {
    const altMatch = /alt="([^"]*)"/.exec(imageMatch[0]);
    images.push({
      src: imageMatch[1],
      alt: altMatch ? altMatch[1] : '',
    });
  }

  const links: Array<{ text: string; href: string }> = [];
  const linkRegex = /<a[^>]+href="([^"]+)"[^>]*>([^<]*)<\/a>/gi;
  let linkMatch;
  while ((linkMatch = linkRegex.exec(html)) !== null) {
    links.push({
      href: linkMatch[1],
      text: linkMatch[2],
    });
  }

  return {
    text,
    codeBlocks,
    images,
    links,
  };
}

export function htmlToMarkdown(html: string): string {
  let markdown = html;

  markdown = markdown.replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, '# $1\n\n');
  markdown = markdown.replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, '## $1\n\n');
  markdown = markdown.replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, '### $1\n\n');
  markdown = markdown.replace(/<p[^>]*>([\s\S]*?)<\/p>/gi, '$1\n\n');
  markdown = markdown.replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, '**$1**');
  markdown = markdown.replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, '**$1**');
  markdown = markdown.replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, '*$1*');
  markdown = markdown.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, (match, p1) => {
    return p1.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, '- $1\n');
  });
  markdown = markdown.replace(/<ol[^>]*>([\s\S]*?)<\/ol>/gi, (match, p1) => {
    let index = 1;
    return p1.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, () => `${index++}. $1\n`);
  });
  markdown = markdown.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1\n```\n');
  markdown = markdown.replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, '`$1`');
  markdown = markdown.replace(/<blockquote[^>]*>([\s\S]*?)<\/blockquote>/gi, '> $1\n');
  markdown = markdown.replace(/<img[^>]+src="([^"]+)"[^>]*>/gi, '![]($1)\n');
  markdown = markdown.replace(/<a[^>]+href="([^"]+)"[^>]*>([^<]*)<\/a>/gi, '[$2]($1)');
  markdown = markdown.replace(/<[^>]+>/g, '');
  markdown = markdown.replace(/\n\s*\n/g, '\n\n');
  markdown = markdown.trim();

  return markdown;
}
