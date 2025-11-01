-- Add conversation_description column to chats.conversation table
-- This column follows the same naming pattern as conversation_title

ALTER TABLE chats.conversation 
ADD COLUMN IF NOT EXISTS conversation_description TEXT;

-- Add comment for documentation
COMMENT ON COLUMN chats.conversation.conversation_description IS 'Description of the conversation (optional text field)';

