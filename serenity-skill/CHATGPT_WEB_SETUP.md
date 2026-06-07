# Using Serenity Skill in ChatGPT Web

ChatGPT web does not automatically load a local Codex skill directory. To use this workflow in ChatGPT, provide the skill as instructions and reference files.

## Best option: ChatGPT Project

Use this when you want an ongoing investment research workspace.

1. Create a new ChatGPT Project.
2. Upload these files as project sources:
   - `SKILL.md`
   - `references/deep-research-workflow.md`
   - `references/evidence-ladder.md`
   - `references/market-source-playbook.md`
   - `references/output-style-and-language.md`
   - `references/risk-and-compliance.md`
3. Add this project instruction:

```text
Use the uploaded serenity-skill workflow for investment research. For single-company research, always map the company's exact value-chain layer, direct competitors, adjacent substitutes, customer chain, supplier chain, cross-industry analogues, where each analogy breaks, evidence quality, failure conditions, and next verification steps. Use public sources and cite them. Give research support only, not trading instructions.
```

## Reusable option: Custom GPT

Use this when you want a dedicated research assistant.

1. Create a GPT in ChatGPT.
2. Paste the core instruction above into the GPT instructions.
3. Upload the same files as Knowledge.
4. Enable web browsing/search if available.
5. Add starters such as:
   - `Use serenity-skill to challenge ASMPT.`
   - `Use serenity-skill to scan the AI advanced packaging chain.`
   - `Compare these companies by chain position and evidence strength.`

## Fast option: One chat

Use this when you only need one research run.

1. Upload `SKILL.md` and the most relevant reference files.
2. Ask:

```text
Read the uploaded serenity-skill files first. Then use that workflow to research [company/theme]. Start with the value-chain layer, scarce layer, comparables, evidence, risks, and next checks.
```

## Maintenance note

When the local skill changes, re-upload the changed files to ChatGPT. ChatGPT web will not automatically sync from `C:\Users\40857\Desktop\Skill\serenity-skill`.
