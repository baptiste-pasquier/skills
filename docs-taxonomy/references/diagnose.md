# Diagnose before restructuring

Run all of these. Write the findings as a numbered list before proposing anything. The
numbers decide the scope, prove the problem to whoever must approve the churn, and usually
show that one or two files are most of it.

**If the append ratio is near 1:1 and no lesson is duplicated, the docs are fine.** Say so
and stop. Restructuring healthy docs is pure cost.

These greps are deliberately cruder than the gate you will build: they do not strip code
fences or backticks, because at this stage you want candidates to read, not verdicts.
Expect false positives from the very files that *state* the rules, and from a `TODO` that
legitimately points at a source-file `TODO`. Read each hit before counting it.

## 1. The append ratio — the headline number

```bash
git log --format='%ad' --date=format:'%Y-%m' --numstat -- docs/ \
  | awk '/^[0-9]{4}-/{m=$0} /^[0-9]+\t/{a[m]+=$1; d[m]+=$2} END{for(k in a) printf "%s +%d -%d\n", k, a[k], d[k]}' \
  | sort
```

Added versus removed, by month. Healthy docs delete as they grow. A ratio above ~5:1 means
nothing is being pruned.

## 2. Which files are the problem

```bash
for f in $(git ls-files 'docs/**/*.md'); do
  printf "%-55s %3s commits  " "$f" "$(git log --oneline -- "$f" | wc -l | tr -d ' ')"
  git log --numstat --format='' -- "$f" | awk '{a+=$1;d+=$2} END{printf "+%d -%d\n", a, d}'
done | sort -k2 -rn
```

A file with many commits and near-zero deletions is a file that has been appended to for
months. That is where the extraction work is.

## 3. Duplicated lessons — the most important finding

Pick a distinctive technical term from each doc and count the files that discuss it:

```bash
grep -rl "<distinctive-term>" docs/ | sed 's|^|  |'
```

Then find the narratives, not just the term:

```bash
grep -rn -iE "used to be|we tried|an earlier version|before this fix|attempts? out of|[0-9]+ (essais?|tentatives?) sur" docs/
```

Three files telling the same story is the signature this skill exists for.

## 4. The cross-link graph

```bash
grep -rn -oE "\]\([^)]*\.md[^)]*\)" docs/ | sed 's/:.*](/ -> /' | sort | uniq -c | sort -rn
```

A **fully connected** graph — every doc links every other — means there is no hierarchy and
no entry point. Check for the entry point directly:

```bash
ls docs/README.md docs/index.md 2>/dev/null || echo "NO INDEX - readers have no way in"
```

## 5. Buried backlog

```bash
grep -rn -iE "not yet implemented|pas encore|TODO|future work|tracked separately|n'est pas implémenté" docs/
```

Every hit is unbuilt work that no tracker knows about. Check each: one may be a real
security or correctness gap that has been sitting in prose.

## 6. Language mixing

```bash
for f in $(git ls-files 'docs/**/*.md'); do
  n=$(grep -cE "\b(le|la|les|une?|des|dans|pour|que|qui|est|sont|cette|pas)\b" "$f")
  printf "%-55s %3s french-ish lines / %s\n" "$f" "$n" "$(wc -l < "$f")"
done
```

Two files in one language and the rest in another, with no stated rule, is drift.

## 7. Prose versus structure

Counting fence lines needs a literal fence marker, so this block is wrapped in four
backticks.

````bash
for f in $(git ls-files 'docs/**/*.md'); do
  fence=$(awk '/^[ \t]*```/{c=!c; next} c{n++} END{print n+0}' "$f")
  printf "%-55s %4s total, %3s in code fences\n" "$f" "$(wc -l < "$f")" "$fence"
done
````

A file that is 250 lines of near-unbroken prose is the illegibility complaint, whatever its
subject.

## 8. Broken links and phantom files

```bash
fail=0
for f in $(git ls-files 'docs/**/*.md'); do
  d=$(dirname "$f")
  for l in $(grep -oE '\]\([^)#]+\.(md|ya?ml)' "$f" | sed 's/^](//'); do
    [ -e "$d/$l" ] || { echo "BROKEN  $f -> $l"; fail=1; }
  done
done
[ $fail -eq 0 ] && echo "all relative links resolve"
```

Also catch inline mentions of files that never existed:

```bash
grep -rn -oE '`[a-z_-]+\.md`' docs/ | sort -u
```

## 9. Internal contradictions

Look for a claim a doc makes about the system that the code contradicts. Cheap version:
grep the docs for enum members, class names and config keys, then check each still exists.

```bash
# example shape - adapt to the project
grep -rn -oE '\b[a-z_]+_(node|schema|prompt)\b' docs/ | sort -u | while read -r hit; do
  sym=${hit##*:}
  git grep -q "$sym" -- src/ || echo "docs mention $sym, absent from src/: $hit"
done
```

## 10. Who else writes into docs/

```bash
ls -d .compound-engineering .cursor .claude 2>/dev/null
grep -rn "docs/" .pre-commit-config.yaml .github/workflows/ Makefile 2>/dev/null | head -20
```

Find the generators and the agent config **before** moving anything. A generated output
path, a docstring, a test assertion and a CI step will all break on a rename, silently.

## 11. Existing gates

```bash
grep -rn -iE "docs|markdown|vale|lychee|mkdocs" .pre-commit-config.yaml .github/workflows/ 2>/dev/null
```

Usually the answer is none. That is the finding: the convention has never been enforced, so
"we will be more careful" has already been tried.
