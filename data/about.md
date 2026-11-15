# About Astraeon

Astraeon is a dashboard that makes NASA's spacecraft fire experiments easy to search, compare and understand. It brings together 24 microgravity combustion investigations from NASA's Physical Sciences Informatics (PSI) repository and checks them against the conditions planned for a Moon base: 30% oxygen or more at 10.2 psi or less.

## What we found

- Only one investigation, ACME CFI-G, has test-by-test records inside the Moon-base zone: 17 hot flames at 33 to 39% ambient oxygen and 7.35 psi. These used gas fuels on a burner, not cabin materials.
- FLEX is a near miss: 17 droplet tests at 30 to 34% oxygen ran at 10.3 to 10.5 psi.
- ACME BRE and FLEX-2 are unconfirmed, because PSI does not record which pressure went with which test.
- No solid cabin material has been fire-tested at Moon-base air in this dataset, and none of the experiments ran in lunar or Martian partial gravity.

## Earth applications

NASA's challenge brief points to four examples of space fire safety research that also helps on Earth: water-mist fire extinguishers used on the International Space Station, a smoke detector developed for the space shuttle that can tell smoke from dust, and firefighter air tanks and protective clothing.

## Data sources

- NASA Physical Sciences Informatics (PSI) repository, psi.nasa.gov: the 24 investigations tagged Combustion Science, linked in the source_link column of each record.
- Oxygen and pressure values were checked against each investigation's experimental table where one exists. The Moon-base check uses 746 flight tests from four experiments.
- Moon-base conditions come from the NASA Space Apps challenge brief.
- Photos are shown only where PSI states a license (CC0-1.0).
- Incident summaries (Apollo 1, Apollo 13 and the Mir fire) cite NASA and other published sources, listed in each entry.

A blank value means the source does not report it. It never means zero.

## How we used AI

- Claude drafted the plain-English summaries, Moon-base takeaways and glossary from the data rows. Every summary was checked by an automated script against its source row (ids, sentence counts and every number) and then read by a team member.
- Claude Code wrote most of the dashboard code with us: the Streamlit pages, styling, charts, the Ask Astraeon search and the checking scripts. We chose the design and the evidence rules, reviewed the output and tested every page.
- The Ask Astraeon page searches only our checked data. When an API key is set, Gemini phrases the answer and cites numbered sources.

## Team

- **Maimuna Afrah** (team lead): data collection and checking, the dashboard, Ask Astraeon, and the final rankings.
- **Ishrat Siddiqui**: AI summaries, glossary, incident history, research gaps, deployment and the submission write-up.
- **Madeeha Khan**: the original relevance rankings.
