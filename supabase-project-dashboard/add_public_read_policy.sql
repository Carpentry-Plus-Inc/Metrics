-- Add public read policy for rhino_blocks table
-- This allows SELECT operations with the anon key while keeping RLS enabled

-- Create policy to allow public read access
CREATE POLICY "Allow public read access to rhino_blocks"
ON rhino_blocks
FOR SELECT
USING (true);

-- Also add the same policy for rhino_breps if it exists
CREATE POLICY "Allow public read access to rhino_breps"
ON rhino_breps
FOR SELECT
USING (true);
