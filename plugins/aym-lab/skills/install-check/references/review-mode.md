# Review mode

Use this to keep the toolkit small after things are installed. It is report-only; the user does every removal themselves.

1. **List what is installed** in each tool you can reach: Claude Code plugins and skills, Codex plugins and skills, MCP connectors and hooks. Say which lists you could not read.
2. **Compare with the toolkit file** (named in the user's instructions, or `~/TOOLKIT.md`; see `SKILL.md`). Flag anything installed but not listed, anything listed but not installed, and any 1-week test date that has passed.
3. **Check the wiring.** Map what each installed skill, plugin and instruction file defines and what it points to. Flag:
   - links and paths that do not resolve, including relative links that only work inside a source repo and break once installed;
   - items nothing points to and nothing triggers;
   - two skills that claim the same trigger phrase;
   - memory or instruction lines that contradict the global instructions or name a removed skill.

   Count always-loaded text (instruction files and every skill description) separately from files read only on demand, since always-loaded text costs every session.
4. **Count real use only.** Count a typed slash command or a model calling the skill. Do not count the skill's file being read. If there is no usage log for a tool, write "no data", not zero; no data is not the same as unused.
5. **Ask two questions per item:** would anything be lost without it (does it do a job nothing else they keep does), and does it earn what it costs (context loaded every session, hooks firing, accounts it can reach)? For any item heading to Remove, ask one more question that tries to prove the verdict wrong, such as "is this the only tool that can reach a service they need?"
6. **Verdict per item:** Keep, Remove, or Merge into one of their skills. Grade overlap with their own skills (such as the aym-* skills) as strong, match, adjacent, weak or conflict. Strong or match means Remove unless the item does something their skill cannot; conflict means the two give opposite instructions and one must go.
7. **Ask one item at a time:** show the evidence (use count, overlap, risk) and your verdict, then ask keep, remove, merge or skip. Collect their answers, then give the exact steps for them to remove the ones they chose and the toolkit file lines to change. Never bulk-remove.
8. **Report** with the stop card described under "4. Report" in `SKILL.md`. `Needs from you:` lists the removals they chose, as steps they can do now.
