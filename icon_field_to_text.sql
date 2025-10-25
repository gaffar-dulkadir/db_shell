-- Change icon field from VARCHAR(500) to TEXT for flexibility
-- This allows both URLs and SVG content
ALTER TABLE marketplace.bot_categories 
ALTER COLUMN icon TYPE TEXT;

-- Update existing data if needed (this is safe as TEXT is larger than VARCHAR)
-- No data migration needed as all VARCHAR data fits in TEXT