INSERT INTO solution_types (name, description, created_at, updated_at)
VALUES
('Unknown', 'Unable to determine connection between clue and solution', datetime('now'), datetime('now')),
('Anagram', 'Letter rearrangement', datetime('now'), datetime('now')),
('Double straight', 'Solution is possible synonym for the (often 2) clue words', datetime('now'), datetime('now')),
('Letter splice', 'Either odd, even or regularly spaced letters from word sequence to form solution', datetime('now'), datetime('now')),
('Partial', 'Partial anagrams requiring subclues', datetime('now'), datetime('now')),
('Double meaning', 'Mis-direction clue word used in wrong context, e.g., flow-er = river', datetime('now'), datetime('now')),
('Sub-words', 'Solution (literally in the clue) found from the end of one clue word and the start of the one following', datetime('now'), datetime('now')),
('Word exchange', 'Solution found from solving mutliple sub clues', datetime('now'), datetime('now')),
('Lucky guess', 'Solution matches one word in the clue, but nothing else', datetime('now'), datetime('now')),
('Subtraction', 'Cue word indicates letters to remove from sub-clue', datetime('now'), datetime('now'));
