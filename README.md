# DSA Progress

Auto-updated by `upload.py`. Use `dsa_manager.py` for daily revision, practice prompts, and local test-case checks.

## DSA Manager

```bash
# Start the browser dashboard at http://127.0.0.1:8000
python3 app.py

# See work due today, then get a concept refresher and next revision problems.
python3 dsa_manager.py dashboard
python3 dsa_manager.py revise

# To re-solve one saved concept, show its complete question immediately.
python3 dsa_manager.py revise checkPrime

# Get a practice problem with constraints and edge cases.
python3 dsa_manager.py list-questions
python3 dsa_manager.py practice --question prime-check

# Generate revision prompts for older saved solutions that do not have one yet.
python3 dsa_manager.py sync-questions

# Check a standalone program or a Solution class against saved tests.
python3 dsa_manager.py check solution.py --question prime-check

# Save a question you create, including its constraints, edge cases, and tests.
python3 dsa_manager.py add-question --id even-number --title "Even Number" --topic Basics --prompt "Print Yes for an even integer, otherwise No." --constraints "-10^9 ≤ n ≤ 10^9" --edge-case "0 is even" --test '{"input":"4\\n","expected":"Yes"}'

# Once you have re-solved a saved problem, schedule its next spaced review.
python3 dsa_manager.py mark-revised "check_prime"
```

Questions and test cases live in `.dsa_questions.json`; add another object there to grow your personal question bank.

When you use `upload.py` for a new solution, it now automatically creates a revision prompt for that problem and stores it in the same question bank. The solution still follows your topic/difficulty folders, for example `03_Arrays/Easy/` or `03_Arrays/Medium/`.

## Summary

| Metric | Value |
| --- | ---: |
| Problems solved | 9 |
| Topics touched | 1 |
| Patterns identified | 1 |
| Last updated | 2026-07-12 17:05 |

## Topic Progress

| Topic | Solved | Progress |
| --- | ---: | --- |
| Basics | 9 | `[####################] 100%` |

## Difficulty

| Difficulty | Solved |
| --- | ---: |
| Easy | 9 |

## Pattern Matching

| Pattern | Problems |
| --- | ---: |
| Math | 9 |

## Revision Queue

| Problem | Topic | Pattern(s) | Revision Due | Status |
| --- | --- | --- | --- | --- |
| check_prime | Basics | Math | 2026-07-13 | Due in 1 day(s) |
| Count_digit | Basics | Math | 2026-07-13 | Due in 1 day(s) |
| Armstrong_check | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| Factor_all_num | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| palindrome_check | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| Check_strong_num | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| Check_prime_num | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| sum_of_digit | Basics | Math | 2026-07-15 | Due in 3 day(s) |
| automorphic_number | Basics | Math | 2026-07-15 | Due in 3 day(s) |

## Recently Solved

| Problem | Topic | Difficulty | Pattern(s) | Updated |
| --- | --- | --- | --- | --- |
| [Armstrong_check](01_Basics/Easy/Armstrong_check.py) | Basics | Easy | Math | 2026-07-12 |
| [Factor_all_num](01_Basics/Easy/Factor_all_num.py) | Basics | Easy | Math | 2026-07-12 |
| [palindrome_check](01_Basics/Easy/palindrome_check.py) | Basics | Easy | Math | 2026-07-12 |
| [Check_strong_num](01_Basics/Easy/Check_strong_num.py) | Basics | Easy | Math | 2026-07-12 |
| [Check_prime_num](01_Basics/Easy/Check_prime_num.py) | Basics | Easy | Math | 2026-07-12 |
| [check_prime](01_Basics/Easy/check_prime.py) | Basics | Easy | Math | 2026-07-12 |
| [sum_of_digit](01_Basics/Easy/sum_of_digit.py) | Basics | Easy | Math | 2026-07-12 |
| [automorphic_number](01_Basics/Easy/automorphic_number.py) | Basics | Easy | Math | 2026-07-12 |
| [Count_digit](01_Basics/Easy/Count_digit.py) | Basics | Easy | Math | 2026-07-10 |
