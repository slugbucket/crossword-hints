INSERT INTO setter_types(name, description, created_at, updated_at)
VALUES
('Normal', 'Good mix of anagrams', datetime('now'), datetime('now')),
('Partial', 'Partial anagrams requiring subclues', datetime('now'), datetime('now')),
('Sly', 'No anagrams, lots of mis-direction', datetime('now'), datetime('now')),
('Hard', 'No obvious match between clues and solutions', datetime('now'), datetime('now')),
("Don't bother", 'No need to waste time trying to decipher', datetime('now'), datetime('now'));
