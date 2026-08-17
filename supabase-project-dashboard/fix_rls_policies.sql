-- Fix RLS policies for rhino_blocks table
-- Run this in your Supabase SQL Editor

-- First, enable RLS on the table (if not already enabled)
ALTER TABLE rhino_blocks ENABLE ROW LEVEL SECURITY;

-- Drop existing policies (if any)
DROP POLICY IF EXISTS "Allow authenticated read" ON rhino_blocks;
DROP POLICY IF EXISTS "Allow authenticated write" ON rhino_blocks;
DROP POLICY IF EXISTS "Allow authenticated insert" ON rhino_blocks;
DROP POLICY IF EXISTS "Allow authenticated update" ON rhino_blocks;
DROP POLICY IF EXISTS "Allow authenticated delete" ON rhino_blocks;

-- Create policies for authenticated users
-- Allow SELECT (read) for authenticated users
CREATE POLICY "Allow authenticated read" 
ON rhino_blocks 
FOR SELECT 
TO authenticated 
USING (true);

-- Allow INSERT for authenticated users
CREATE POLICY "Allow authenticated insert" 
ON rhino_blocks 
FOR INSERT 
TO authenticated 
WITH CHECK (true);

-- Allow UPDATE for authenticated users
CREATE POLICY "Allow authenticated update" 
ON rhino_blocks 
FOR UPDATE 
TO authenticated 
USING (true) 
WITH CHECK (true);

-- Allow DELETE for authenticated users
CREATE POLICY "Allow authenticated delete" 
ON rhino_blocks 
FOR DELETE 
TO authenticated 
USING (true);

-- Allow anonymous (anon) users to READ only (needed for Streamlit dashboard)
CREATE POLICY "Allow anonymous read" 
ON rhino_blocks 
FOR SELECT 
TO anon 
USING (true);
