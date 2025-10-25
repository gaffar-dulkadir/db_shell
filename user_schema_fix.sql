-- Add missing fields to auth.users table
ALTER TABLE auth.users 
ADD COLUMN IF NOT EXISTS username VARCHAR(100) UNIQUE,
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'active',
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Create unique index for username (excluding NULL values)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username 
ON auth.users (username) 
WHERE username IS NOT NULL;

-- Add check constraint for status enum
ALTER TABLE auth.users 
ADD CONSTRAINT IF NOT EXISTS chk_user_status 
CHECK (status IN ('active', 'inactive', 'suspended'));

-- Update existing users to have default values
UPDATE auth.users 
SET 
    is_verified = true,  -- Mark existing users as verified
    status = 'active'    -- Mark existing users as active
WHERE is_verified IS NULL OR status IS NULL;