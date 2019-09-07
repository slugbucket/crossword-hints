INSERT INTO setter_types(name, description, created_at, updated_at)
VALUES
('Normal', 'Good mix of anagrams', datetime('now'), datetime('now')),
('Partial', 'Partial anagrams requiring subclues', datetime('now'), datetime('now')),
('Sly', 'No anagrams, lots of mis-direction', datetime('now'), datetime('now')),
('Hard', 'No obvious match between clues and solutions', datetime('now'), datetime('now')),
("Don't bother", 'No need to waste time trying to decipher', datetime('now'), datetime('now'));

INSERT INTO crossword_setters(name, setter_type_id, description, created_at, updated_at)
VALUES
('Anarche', '4', 'Unrewarding and easily distracted elsewhere', datetime('now'), datetime('now')),
('Crosophile', '3', 'Solvable and more enjoyable then many', datetime('now'), datetime('now')),
('Dac', '4', 'A rewarding blend and occasionally solvable', datetime('now'), datetime('now')),
('Eimi', '2', 'Sometimes solvable; worth an hour or so', datetime('now'), datetime('now')),
('Glow-worm', '4', 'Unrewarding and easily distracted elsewhere', datetime('now'), datetime('now')),
('Hypnos', '4', 'Worth a peek if you can find a way in', datetime('now'), datetime('now')),
('Klingsor', '5', 'A few clues perhaps', datetime('now'), datetime('now')),
('Monk', '4', 'Not even solvable with the solutions', datetime('now'), datetime('now')),
('Mordred', '4', 'Is that the washing-up that needs doing?', datetime('now'), datetime('now')),
('Morph', '4', 'Unrewarding and easily distracted elsewhere', datetime('now'), datetime('now')),
('Nestor', '5', 'A couple of hours of your life you''re never getting back', datetime('now'), datetime('now')),
('Phi', '1', 'Anagrammatic joy', datetime('now'), datetime('now')),
('Poins', '4', 'And you wanted something to pass the time on a long journey', datetime('now'), datetime('now')),
('Punk', '5', 'For hardcore wordplay fans. Avoid', datetime('now'), datetime('now')),
('Quixote', '2', 'A relaxing way to unwind at the end of the day', datetime('now'), datetime('now')),
('Radian', '4', 'Rewarding if you can crack the theme', datetime('now'), datetime('now')),
('Raich', '4', 'The theme is usually out of reach', datetime('now'), datetime('now')),
('Scorpion', '5', 'For hardcore wordplay fans. Avoid', datetime('now'), datetime('now')),
('Tees', '5', 'An opportunity for some doodling practice.', datetime('now'), datetime('now')),
('eXternal', '5', 'A fair bit of wordplay', datetime('now'), datetime('now')),
('Hieroglyph', '5', 'Sometimes gently themed puzzles', datetime('now'), datetime('now'));

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
('Word insertion', 'Insert one answer to a sub-clue into another.', datetime('now'), datetime('now')),
('Homophone', 'Sounds like', datetime('now'), datetime('now'));

INSERT INTO cue_words(cue_word, meaning, created_at, updated_at) values
("primarily", "Take the first letter(s) of surrounding word(s)", datetime('now'), datetime('now')),
("initially", "Take the first letter(s) of surrounding words(s)", datetime('now'), datetime('now')),
("starts", "Take the first letter(s) of surrounding words(s)", datetime('now'), datetime('now')),
("partially", "a few letter of", datetime('now'), datetime('now')),
("oddly", "every other letter starting from the first", datetime('now'), datetime('now')),
("evenly", "2nd, 4th, 6th, ... letters", datetime('now'), datetime('now')),
("almost", "not quite all of the word", datetime('now'), datetime('now')),
("decapitate", "remove first letter", datetime('now'), datetime('now')),
("most of", "remove last letter", datetime('now'), datetime('now')),
("unfinished", "remove last letter", datetime('now'), datetime('now')),
("mostly", "not quite all of the word", datetime('now'), datetime('now')),
("somewhat", "last letters of one word with the first letters of the next", datetime('now'), datetime('now')),
("part of", "last letters of one word with the first letters of the next", datetime('now'), datetime('now')),
("out of", "last letters of one word with the first letters of the next", datetime('now'), datetime('now')),
("penned", "last letters of one word with the first letters of the next", datetime('now'), datetime('now')),
("sorted", "anagram indicator", datetime('now'), datetime('now')),
("mixed", "anagram indicator", datetime('now'), datetime('now')),
("confused", "anagram indicator", datetime('now'), datetime('now')),
("confusing", "anagram indicator", datetime('now'), datetime('now')),
("strange", "anagram indicator", datetime('now'), datetime('now')),
("strangely", "anagram indicator", datetime('now'), datetime('now')),
("turmoil", "anagram indicator", datetime('now'), datetime('now')),
("muddled", "anagram indicator", datetime('now'), datetime('now')),
("broken", "anagram indicator", datetime('now'), datetime('now')),
("fixed", "anagram indicator", datetime('now'), datetime('now')),
("trips", "anagram indicator", datetime('now'), datetime('now')),
("shattered", "anagram indicator", datetime('now'), datetime('now')),
("oddball", "anagram indicator", datetime('now'), datetime('now')),
("criminal", "anagram indicator", datetime('now'), datetime('now')),
("outrageous", "anagram indicator", datetime('now'), datetime('now')),
("rebuilt", "anagram indicator", datetime('now'), datetime('now')),
("possibly", "anagram indicator", datetime('now'), datetime('now')),
("whipped", "anagram indicator", datetime('now'), datetime('now')),
("whip", "anagram indicator", datetime('now'), datetime('now')),
("extreme", "first and/or last letter(s)", datetime('now'), datetime('now')),
("extremely", "first and/or last letter(s)", datetime('now'), datetime('now')),
("casing", "first and/or last letter(s)", datetime('now'), datetime('now')),
("outside", "first and/or last letter(s)", datetime('now'), datetime('now')),
("topless", "remove first letter", datetime('now'), datetime('now')),
("left", "first letter or L", datetime('now'), datetime('now')),
("right", "last letter or right", datetime('now'), datetime('now')),
("port", "L (for left)", datetime('now'), datetime('now')),
("shocking", "anagram indicator", datetime('now'), datetime('now')),
("blown up", "anagram indicator", datetime('now'), datetime('now')),
("twisted", "anagram indicator", datetime('now'), datetime('now')),
("nasty", "anagram indicator", datetime('now'), datetime('now')),
("centre", "letters ", datetime('now'), datetime('now')),
("central", "middle letters", datetime('now'), datetime('now')),
("heart", "middle letters", datetime('now'), datetime('now')),
("marrow", "middle letters", datetime('now'), datetime('now')),
("change of heart", "swap middle letters", datetime('now'), datetime('now')),
("heartless", "excluding the middle letters", datetime('now'), datetime('now')),
("supported", "appears at the end", datetime('now'), datetime('now')),
("shortly", "removed letter from the end of", datetime('now'), datetime('now')),
("leader", "first letter", datetime('now'), datetime('now')),
("leaders", "first letter from a sequence of words", datetime('now'), datetime('now')),
("awkward", "anagram indicator", datetime('now'), datetime('now')),
("loud", "F", datetime('now'), datetime('now')),
("loudly", "FF", datetime('now'), datetime('now')),
("noisily", "FF", datetime('now'), datetime('now')),
("very loud", "FF", datetime('now'), datetime('now')),
("quiet", "P or SH", datetime('now'), datetime('now')),
("quietly", "PP", datetime('now'), datetime('now')),
("upset", "anagram indicator", datetime('now'), datetime('now')),
("wrecked", "anagram indicator", datetime('now'), datetime('now')),
("battered", "anagram indicator", datetime('now'), datetime('now')),
("smashed", "anagram indicator", datetime('now'), datetime('now')),
("mashed", "anagram indicator", datetime('now'), datetime('now')),
("knitted", "anagram indicator", datetime('now'), datetime('now')),
("perverse", "anagram indicator", datetime('now'), datetime('now')),
("forged", "anagram indicator", datetime('now'), datetime('now')),
("intrinsically", "anagram indicator", datetime('now'), datetime('now')),
("drunk", "anagram indicator", datetime('now'), datetime('now')),
("fixing", "anagram indicator", datetime('now'), datetime('now')),
("reflection", "write the letters backwards", datetime('now'), datetime('now')),
("capsized", "reverse the letter order", datetime('now'), datetime('now')),
("north", "N", datetime('now'), datetime('now')),
("northerly", "reverse the letter order", datetime('now'), datetime('now')),
("going north", "reverse the letter order", datetime('now'), datetime('now')),
("sent back", "write the letters backwards", datetime('now'), datetime('now')),
("university", "U", datetime('now'), datetime('now')),
("open-ended", "remove first and last letters", datetime('now'), datetime('now')),
("top to bottom", "Move the first letter to the end", datetime('now'), datetime('now')),
("top to tail", "Move the first letter to the end", datetime('now'), datetime('now')),
("front to back", "Move the first letter to the end", datetime('now'), datetime('now')),
("back to front", "Move the last letter to the front", datetime('now'), datetime('now')),
("cycling", "Move the last letter to the front, or vice versa", datetime('now'), datetime('now')),
("missing", "letters removed", datetime('now'), datetime('now')),
("tip", "First or last letter", datetime('now'), datetime('now')),
("edges", "The first and last letter", datetime('now'), datetime('now')),
("endlessly", "Remove the first and last letter", datetime('now'), datetime('now')),
("exclude", "Remove a particular letter", datetime('now'), datetime('now')),
("nearly", "Remove the last letter", datetime('now'), datetime('now')),
("introduction", "first letter", datetime('now'), datetime('now')),
("glasses", "OO", datetime('now'), datetime('now')),
("spectacle", "OO", datetime('now'), datetime('now')),
("obscene", "BLUE", datetime('now'), datetime('now')),
("good", "G", datetime('now'), datetime('now')),
("cockney", "drop an H", datetime('now'), datetime('now')),
("thus", "SO", datetime('now'), datetime('now')),
("almost", "AL", datetime('now'), datetime('now')),
("introducing", "before", datetime('now'), datetime('now')),
("old boy", "OB", datetime('now'), datetime('now')),
("speed", "MPH", datetime('now'), datetime('now')),
("love", "O", datetime('now'), datetime('now')),
("on", "RE", datetime('now'), datetime('now')),
("about", "RE or surrounding", datetime('now'), datetime('now')),
("greens", "BUCKS", datetime('now'), datetime('now')),
("hard", "H", datetime('now'), datetime('now')),
("street", "ST", datetime('now'), datetime('now')),
("ewe", "YOU or U (homophone or sounds like)", datetime('now'), datetime('now')),
("overheard", "homophone, sounds like", datetime('now'), datetime('now')),
("wanting", "remove letters", datetime('now'), datetime('now')),
("abandon", "remove letters", datetime('now'), datetime('now')),
("gutted", "remove letters from middle of word", datetime('now'), datetime('now')),
("abandoning", "remove letters", datetime('now'), datetime('now')),
("bass", "B", datetime('now'), datetime('now')),
("electronic", "E", datetime('now'), datetime('now')),
("double", "repeat letter", datetime('now'), datetime('now')),
("work", "OP or anagram indicator", datetime('now'), datetime('now')),
("method", "OM", datetime('now'), datetime('now')),
("relief", "AID", datetime('now'), datetime('now')),
("soldiers", "MEN, RE", datetime('now'), datetime('now')),
("army", "MEN, RE", datetime('now'), datetime('now')),
("chief", "HEAD", datetime('now'), datetime('now')),
("old man", "PA", datetime('now'), datetime('now')),
("wife", "W", datetime('now'), datetime('now')),
("sailor", "AB, TAR, RN, RM", datetime('now'), datetime('now')),
("powerless", "remove letter P", datetime('now'), datetime('now')),
("prisoner", "LIFER or CON", datetime('now'), datetime('now')),
("iron", "FE", datetime('now'), datetime('now')),
("sandwiches", "contains", datetime('now'), datetime('now')),
("boxes", "contains", datetime('now'), datetime('now')),
("nothing", "O", datetime('now'), datetime('now')),
("just", "FAIR", datetime('now'), datetime('now')),
("light", "FAIR", datetime('now'), datetime('now')),
("chum", "PAL", datetime('now'), datetime('now')),
("friend", "PAL", datetime('now'), datetime('now')),
("mate", "PAL", datetime('now'), datetime('now')),
("buddy", "PAL", datetime('now'), datetime('now')),
("writer", "PEN, I or ME", datetime('now'), datetime('now')),
("solicit", "TOUT", datetime('now'), datetime('now')),
("solicitor", "TOUT", datetime('now'), datetime('now')),
("railway", "RY", datetime('now'), datetime('now')),
("hot", "H", datetime('now'), datetime('now')),
("penny", "D", datetime('now'), datetime('now')),
("pennies", "DD", datetime('now'), datetime('now')),
("article", "A, AN or THE", datetime('now'), datetime('now')),
("interrupt", "insert sub-clue solution", datetime('now'), datetime('now')),
("say", "homophone indicator", datetime('now'), datetime('now')),
("sounded", "homophone indicator", datetime('now'), datetime('now')),
("bank", "TIER", datetime('now'), datetime('now')),
("theatre", "REP", datetime('now'), datetime('now')),
("exist", "BE", datetime('now'), datetime('now')),
("gangster", "AL", datetime('now'), datetime('now')),
("old woman", "WITCH, BAT, HAG", datetime('now'), datetime('now')),
("former", "EX", datetime('now'), datetime('now')),
("erstwhile", "EX", datetime('now'), datetime('now')),
("religious", "PI", datetime('now'), datetime('now')),
("ex-officio", "EO", datetime('now'), datetime('now')),
("police", "COP", datetime('now'), datetime('now')),
("monarch", "ER", datetime('now'), datetime('now')),
("queen", "ER", datetime('now'), datetime('now')),
("bishop", "B or RR", datetime('now'), datetime('now')),
("head", "first letter of previous word", datetime('now'), datetime('now')),
("eventually", "last letter", datetime('now'), datetime('now'));

INSERT INTO crossword_solutions(crossword_setter_id, clue, solution, solution_hint, solution_type_id, created_at, updated_at) VALUES
("2", "Cross off TV cabinet", "dresser", "", "1", datetime('now'), datetime('now')),
("2", "An element of extra backsliding - a period that's not over", "sulphur", "", "1", datetime('now'), datetime('now')),
("2", "Axe bush", "scrub", "", "3", datetime('now'), datetime('now')),
("2", "Initially every girl's ornment for navy dress ...", "epaulette", "", "9", datetime('now'), datetime('now')),
("2", "... celebrated by girls in shades", "sunglasses", "celebrated = SUNG + girls = LASSES", "8", datetime('now'), datetime('now')),
("2", "Spirit in the heart of Maori country", "zeal", "new-ZEAL-and", "7", datetime('now'), datetime('now')),
("2", "Broadcast item: Bridge players shot at home", "news bulletin", "", "1", datetime('now'), datetime('now')),
("2", "Coped with payment for organising surgical operation", "appendectomy", "", "2", datetime('now'), datetime('now')),
("2", "Corner that is cut off from relations", "nook", "", "8", datetime('now'), datetime('now')),
("2", "Tumble on this, parking ball inside edge of tennis court", "trampoline", "TRAM-P-O-LINE", "8", datetime('now'), datetime('now')),
("2", "He sold ale at sea, an occupation agreed by letter", "leasehold", "", "2", datetime('now'), datetime('now')),
("2", "Is he engaged in activity of collecting information?", "agent", "", "9", datetime('now'), datetime('now')),
("2", "Given warning related to the work", "alerted", "", "2", datetime('now'), datetime('now')),
("2", "The opening of a flower", "estuary", "FLOW-ER i.e., river", "6", datetime('now'), datetime('now')),
("2", "To stop believing in God takes a touch of scepticism", "desist", "", "9", datetime('now'), datetime('now')),
("2", "Ruin envelopes cleric and Mendoza finally in the Mission", "errand", "", "9", datetime('now'), datetime('now')),
("2", "Junior officers in coach reversing - shift to neutral then second", "subalterns", "", "5", datetime('now'), datetime('now')),
("2", "Rising sun does maybe in the grasses", "reeds", "Rising means revers, DOEs = deer", "6", datetime('now'), datetime('now')),
("2", "What to wear if no atmosphere in club, for instance, taking steps", "spacesuit", "", "5", datetime('now'), datetime('now')),
("2", "Spirited heartless girl", "lily", "", "1", datetime('now'), datetime('now')),
("2", "Knocked Achilles, say around Troy and as far as this", "hitherto", "", "1", datetime('now'), datetime('now')),
("2", "Wine lies split in a circle", "riesling", "R-IESL-ING, RING = circle", "5", datetime('now'), datetime('now')),
("2", "Extravagant husband entertains son in apartment", "flamboyant", "FLA-m-BOY-an-T", "8", datetime('now'), datetime('now')),
("2", "Military force has to display oath", "swearword", "S-wear-WORD", "8", datetime('now'), datetime('now')),
("2", "With intention to pot stretched out amateur returning for colour off white", "magnolia", "", "9", datetime('now'), datetime('now')),
("2", "Like a palm tree climber's hip?", "up to date", "HIP = up to date, which is where tree climbers go", "6", datetime('now'), datetime('now')),
("2", "At home in church with mother where Rebecca and Arthur might be seen", "cinema", "", "1", datetime('now'), datetime('now')),
("2", "The lowdown to have a go at the upper classes", "gentry", "GEN = lowdown, TRY = have a go", "8", datetime('now'), datetime('now')),
("2", "Bloodsucker appears as cloud rises", "midge", "", "9", datetime('now'), datetime('now')),
("2", "Hide from downpour", "pelt", "", "3", datetime('now'), datetime('now')),
("2", "Notice political parties unscripted comments", "ad-libs", "AD = notice", "8", datetime('now'), datetime('now')),
("2", "Constant pressure here, I cry with a touch of rancour", "isobar", "I-SOB(=cry)-AR", "8", datetime('now'), datetime('now')),
("2", "Guys steady this explosion packed with earth", "tent", "Guy ropes steady a TENT into earth", "6", datetime('now'), datetime('now')),
("2", "Ruin ends in penury - turn back from this", "bankruptcy", "", "9", datetime('now'), datetime('now')),
("2", "Parts of garlic and henbane spliced two plants in one", "lichen", "garLIC HENbane", "4", datetime('now'), datetime('now')),
("2", "With two feet cut, start to see about a doctors instrument", "bagpipes", "", "1", datetime('now'), datetime('now')),
("2", "Uniform advice crossed out by the returning journalist", "dress code", "rearranged CROSSED + journalist = ED", "5", datetime('now'), datetime('now')),
("2", "Greek characters fully satisfy on reflection", "etas", "reflection = reverse for SATE", "6", datetime('now'), datetime('now')),
("2", "Inside Holy Land?", "acre", "ACRE is a Holy town and a unit of land", "3", datetime('now'), datetime('now')),
("2", "Dinosaur's marrow to signify broken bone-setting?", "ossifying", "the middle (marrow) of dinOSaur with rearrangement of signify", "9", datetime('now'), datetime('now')),
("2", "Out, when unwell, without a tissue? Cheers", "thank you", "rearranged OUT + HANKY", "6", datetime('now'), datetime('now')),
("2", "Result of troubles in Northern Ireland", "ulster", "Anagram of result", "2", datetime('now'), datetime('now')),
("2", "Skilled worker - one in oil company at inception of two parties", "bipartisan", "", "1", datetime('now'), datetime('now')),
("2", "Maybe porter carrying Times wheels around this", "axle", "porter = ALE, with (carrying) X (times) inside", "6", datetime('now'), datetime('now')),
("2", "2 letters or 9?", "teepee", "T & P are two letters; it is also a TENT, the solution to 9a", "6", datetime('now'), datetime('now')),
("2", "They show way to remove power from drug dealers", "ushers", "Remove P from PUSHERS", "8", datetime('now'), datetime('now')),
("2", "Took in story told by reading or writing workshop?", "atelier", "", "1", datetime('now'), datetime('now')),
("2", "Trainee pilots moving into left hand lock", "latch", "trainee pilot = ATC inside L and H to give a lock", "8", datetime('now'), datetime('now')),
("2", "About brown mince, avoid odd bits like the plague", "bubonic", "avoid odd letters in aBoUtBrOwNmInCe", "4", datetime('now'), datetime('now')),
("2", "Brushes off edges of swish carpets", "shrugs", "brush off = SHRUG, edges of SwisH + RUGS (carpets", "8", datetime('now'), datetime('now')),
("2", "Font's seen here in book - is it following appropriate lines?", "baptistry", "", "1", datetime('now'), datetime('now')),
("2", "Sign of deficiency in headless insects", "rickets", "remove first letter from cRICKETS", "8", datetime('now'), datetime('now')),
("2", "Who knows a song by Debussy composed with only one bass part?", "anybodys guess", "", "5", datetime('now'), datetime('now')),
("2", "Psychoanalysis, perhaps, the result of pilfering?", "shrinkage", "", "9", datetime('now'), datetime('now')),
("2", "Infidel involved in armed robbery", "atheist", "Infidel = non-believer, AT (involved) + HEIST (armed robbery)", "8", datetime('now'), datetime('now')),
("2", "Island full of lots of bird dung and Australian lizards", "iguanas", "", "9", datetime('now'), datetime('now')),
("2", "Taunts mostly unnecessary", "needles", "most of NEEDLESs", "6", datetime('now'), datetime('now')),
("2", "Fragrant shrub's attempt to climb up into flipping tree", "myrtle", "TRY in reverse (climbing up) inside ELM revered (flipping)", "8", datetime('now'), datetime('now')),
("2", "Ghost from the underworld, the last to rise up", "shade", "S (last) from HADES rises up (to the front)", "6", datetime('now'), datetime('now')),
("2", "Centre for climber association providing for mountainous region", "massif", "", "9", datetime('now'), datetime('now')),
("2", "Feeble nonsense that's a threat to the house?", "wet rot", "feeble = WET + nonsense = ROT", "8", datetime('now'), datetime('now')),
("2", "It's ignorant to see a conflict between even funnier characters", "unaware", "", "9", datetime('now'), datetime('now')),
("2", "Only very noisy vehicle going round and round? More than that", "traffic", "", "1", datetime('now'), datetime('now')),
("2", "Daringly, when a ring is replaced by old boat - at night?", "darkly", "", "1", datetime('now'), datetime('now')),
("2", "Child is caught by cunning, a flaming nuisance", "arsonist", "", "9", datetime('now'), datetime('now')),
("2", "Protected from canine attack", "armed to the teeth", "", "6", datetime('now'), datetime('now')),
("2", "I won't say I'm sparely fashioned - a vast mass under control", "my lips are sealed", "", "6", datetime('now'), datetime('now')),
("2", "Sort out any hitch or bloomer", "hyacinth", "", "2", datetime('now'), datetime('now')),
("2", "Mushroom and a main ingredient of aioli left out", "agaric", "", "9", datetime('now'), datetime('now')),
("2", "Spooner's heard of fleece coming from salmon? That's desirable if not likely", "wishful", "", "1", datetime('now'), datetime('now')),
("2", "Caught Sibyl's little boat", "coracle", "", "8", datetime('now'), datetime('now')),
("2", "What to do if stuck in tropical forest with leader lost (stabbed by tip of urari)", "unglue", "", "1", datetime('now'), datetime('now')),
("2", "Singer's dishertening quaver?", "treble", "quaver = TREmBLE with the middle (heart) removed", "6", datetime('now'), datetime('now')),
("2", "A horse and tup put ashore for example?", "anagram", "A + horse = NAG + tup = RAM", "8", datetime('now'), datetime('now')),
("2", "Unhappy about location of shops being classified information", "small ad", "unhappy = SAD, with MALL", "6", datetime('now'), datetime('now')),
("2", "Run off a small jumper say", "flee", "Sounds like (say) flea", "6", datetime('now'), datetime('now')),
("2", "Ground wheat with reel that powers mill?", "water wheel", "", "2", datetime('now'), datetime('now')),
("2", "Fruit in all of Normandy to go slushy?", "thaw out", "", "9", datetime('now'), datetime('now')),
("2", "Poorly fed - if so slips may be seen here", "off side", "", "2", datetime('now'), datetime('now')),
("2", "Barrel's 'eavy when lifted - it's just plain frozen", "tundra", "", "9", datetime('now'), datetime('now')),
("2", "Put the lid on whisky", "scotch", "", "9", datetime('now'), datetime('now')),
("2", "Carbon-based rock crushed black's left in original tube as artist's pigment", "cobalt blue", "", "5", datetime('now'), datetime('now')),
("2", "Some crayfish that'll live in saltwater", "ray", "cRAYfish", "4", datetime('now'), datetime('now')),
("2", "Little piggy regularly sampled Pot Noodles", "toe", "poTnoOdlEs", "4", datetime('now'), datetime('now')),
("2", "An Iroquois way of working with bird of prey", "mohawk", "MO = way of working, HAWK = bird of prey", "8", datetime('now'), datetime('now')),
("2", "Trouble over one relative's affair", "liaison", "", "1", datetime('now'), datetime('now')),
("2", "How it might feel if I dipped into water on hob?", "painful", "", "1", datetime('now'), datetime('now')),
("2", "Call for protective measures in fencing, often garden fences", "en garde", "oftEN GARDEn", "4", datetime('now'), datetime('now')),
("2", "When dancing, I cry, all can be expressive", "lyrical", "ICRYALL", "2", datetime('now'), datetime('now')),
("2", "Duke's more hostile and more dangerous", "dicier", "D + ICIER (more hostile)", "8", datetime('now'), datetime('now')),
("2", "Genuine German playwright, not British", "echt", "brECHT - BRitish", "10", datetime('now'), datetime('now')),
("2", "Lay cryptic clues before adult readers primarily", "secular", "rearrange CLUES + Adult Readers (primariy)", "4", datetime('now'), datetime('now')),
("2", "Fabrication by Feds planted in course of seizure", "figment", "", "9", datetime('now'), datetime('now')),
("2", "Commander having office once more", "again", "commander = AGA + having office = IN", "8", datetime('now'), datetime('now')),
("2", "Second employment: recurring role in long-running play", "mousetrap", "", "9", datetime('now'), datetime('now')),
("2", "Home team penetrates defence that's not brilliant with run for header", "residence", "", "1", datetime('now'), datetime('now')),
("2", "Top of tree's odd trunk", "torso", "", "9", datetime('now'), datetime('now')),
("2", "Peas or leeks broadcast round bottom of field are unwanted plants", "weeds", "WEE = pee or (take a ) leak), broadcast = surround, bottom of field = D", "8", datetime('now'), datetime('now')),
("2", "Court charges resulting in bird", "spoonbill", "", "9", datetime('now'), datetime('now')),
("2", "Will trial endorse Chilcott's conclusion?", "testament", "", "1", datetime('now'), datetime('now')),
("2", "Have a doss when Skins is over", "sleep", "", "1", datetime('now'), datetime('now')),
("2", "Fantastic tangle holding you French back", "outre", "UT = you (in) French back (reversed)", "9", datetime('now'), datetime('now')),
("2", "Reckless idiot half of double act", "foolhardy", "idiot = FOOL, half of double act = HARDY", "8", datetime('now'), datetime('now')),
("2", "'Royal Highness' is out of line by dressing down", "talking to", "", "9", datetime('now'), datetime('now')),
("2", "In Two Thousand And One, its computer is cut off - this is dull material", "khaki", "KKI = 2001, HAl is computer cut off", "10", datetime('now'), datetime('now')),
("2", "Full theatre's licensed revue at last", "replete", "REP (theatre) + LET (licensed) + revuE (last)", "8", datetime('now'), datetime('now')),
("2", "Amateur mercenaries save 100 pounds", "hammers", "HAM (amateur?) + MERcenaries + S, pounds != weight", "6", datetime('now'), datetime('now')),
("2", "Special pointer finds bird", "sparrow", "SPecial + ARROW (pointer)", "8", datetime('now'), datetime('now')),
("2", "Egalitarian girl is non-U clues by us", "classless", "girl = LASS + CLuES + uS (non-U)", "9", datetime('now'), datetime('now')),
("2", "Series of descendants with crown of David ruled", "lined", "", "9", datetime('now'), datetime('now')),
("2", "Remember, put little old car in salvage (it has no fifth)", "reminisce", "", "1", datetime('now'), datetime('now')),
("2", "Musical instrument - loud one", "flute", "", "9", datetime('now'), datetime('now')),
("2", "Welcome hints of tomato in garlic sprinkled into cabbage", "greetings", "cabbage = GREENS with Tomato + Garlic, other bits missing", "9", datetime('now'), datetime('now')),
("2", "Losing head, panic by mistake", "error", "tERROR (panic losing first letter - head)", "3", datetime('now'), datetime('now')),
("2", "Fertile layer split two eggs - scrambled", "topsoil", "SPLIT + O + O (two eggs)", "5", datetime('now'), datetime('now')),
("2", "Nasty wound - bike seat needs adjusting round bearing", "snakebite", "BIKE + SEAT + N (bearing)", "5", datetime('now'), datetime('now')),
("2", "For translation go to short old German", "ostrogoth", "translation = anagram", "2", datetime('now'), datetime('now')),
("2", "I'll go with last of gin, beer and one tequila for starters in a cocktail", "inebriate", "", "1", datetime('now'), datetime('now')),
("2", "Tango with cad and heel (pig!)", "trotter", "Tango + ROTTER (cad)", "10", datetime('now'), datetime('now')),
("2", "Science of jography (sic) studies", "physics", "jograPHY-SIC-Studies", "7", datetime('now'), datetime('now')),
("2", "Put out lit-up bulb", "tulip", "", "2", datetime('now'), datetime('now')),
("2", "Finally oddly used to stuffiness in composition", "fugue", "", "9", datetime('now'), datetime('now')),
("2", "Theatrical claptrap is certainly in bad odeur", "hokum", "certainly = OK, bad odeur = HUM", "8", datetime('now'), datetime('now')),
("2", "Salome? Not, you ultimately suspect, the perfect partner", "soul mate", "noT yoU (ultimately) + SALOME rearranged", "5", datetime('now'), datetime('now')),
("2", "Remove casings from lock, pull and push, and make eye-like opening", "oculus", "lOCk-pULl-pUSh (remove casings)", "4", datetime('now'), datetime('now')),
("2", "Hardy female stresses regular scrubbings", "tess", "sTrEsSeS", "4", datetime('now'), datetime('now')),
("2", "Web developer's unhappy with marriage vow and wife", "black widow", "", "6", datetime('now'), datetime('now')),
("2", "Finally having scope to make first move", "gambit", "", "1", datetime('now'), datetime('now')),
("2", "Strut round, getting girl's offer of marriage", "proposal", "PROP-O-SAL, support-round-girl", "8", datetime('now'), datetime('now')),
("2", "Old boy endures retirement with Player's No. 6, small canine and extremely hot soup", "borscht", "", "9", datetime('now'), datetime('now')),
("2", "Sent mob to blow up sepulchres", "entombs", "", "2", datetime('now'), datetime('now')),
("2", "Never, ever salaciously describe misfortune!", "reversal", "neveR-EVER-SALaciously", "4", datetime('now'), datetime('now')),
("2", "Date lad who always goes home to bed", "day boy", "", "1", datetime('now'), datetime('now')),
("2", "Two nestled together, prepared to do this?", "settle down", "", "2", datetime('now'), datetime('now')),
("2", "Possessions essentially taken to be objects of worship", "gods", "Possibly GOoDS", "9", datetime('now'), datetime('now')),
("2", "Kind of acid mostly found in kernels", "nuclei", "", "1", datetime('now'), datetime('now')),
("2", "Romeo's beginning to go terribly pale in vault", "overleap", "", "1", datetime('now'), datetime('now')),
("2", "Many uplifting books are read at medium speed", "moderato", "", "9", datetime('now'), datetime('now')),
("2", "Otherwise known as 'missing individual', sadly", "alas", "", "9", datetime('now'), datetime('now')),
("2", "Join rear admiral and bishop in punt", "rabbet", "", "9", datetime('now'), datetime('now')),
("2", "Makes improvements to her technique at last and seduces men", "revamps", "", "9", datetime('now'), datetime('now')),
("2", "Man surrounded by noise in far-off Civil War battle", "yorktown", "", "9", datetime('now'), datetime('now')),
("2", "Smug, oily bastard accepting firm, sound discipline", "musicology", "SMUG+OILY, frim = CO", "5", datetime('now'), datetime('now')),
("2", "Heartless user finding love with old man under English moon", "europa", "", "9", datetime('now'), datetime('now')),
("2", "Relative's reactionary steps to restrain former partner in lear year", "bisextile", "", "1", datetime('now'), datetime('now')),
("2", "This year could produce emotional meltdown", "hysteria", "THIS YEAR", "2", datetime('now'), datetime('now')),
("2", "Really supportive of dame in theatrical drag", "broadway", "", "1", datetime('now'), datetime('now')),
("2", "Coppola production which is sweetly intoxicating", "alcopop", "", "2", datetime('now'), datetime('now')),
("2", "Initially extraordinary year especailly for unmarried lady who's a beauty", "eyeful", "First letter of each word", "4", datetime('now'), datetime('now')),
("2", "Back in Eden nudists were importunate", "dunned", "", "1", datetime('now'), datetime('now')),
("2", "Young woman needs answer to be fair", "gala", "GAL = young woman, A = answer", "6", datetime('now'), datetime('now'));

INSERT INTO users(username, created_at, updated_at) VALUES
('xword', datetime('now'), datetime('now'));
