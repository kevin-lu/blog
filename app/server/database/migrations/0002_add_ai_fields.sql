-- Add AI-related fields to article_meta table
ALTER TABLE article_meta ADD COLUMN source_url TEXT;
ALTER TABLE article_meta ADD COLUMN ai_generated INTEGER DEFAULT 0;
ALTER TABLE article_meta ADD COLUMN ai_model TEXT;
ALTER TABLE article_meta ADD COLUMN rewrite_strategy TEXT DEFAULT 'standard';
ALTER TABLE article_meta ADD COLUMN template_type TEXT DEFAULT 'tutorial';
ALTER TABLE article_meta ADD COLUMN word_count INTEGER;
ALTER TABLE article_meta ADD COLUMN auto_published INTEGER DEFAULT 0;

-- Create index for AI-generated articles
CREATE INDEX IF NOT EXISTS idx_article_ai_generated ON article_meta(ai_generated);
CREATE INDEX IF NOT EXISTS idx_article_source_url ON article_meta(source_url);
