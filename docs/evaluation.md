# Evaluation: Known-Item Sanity Test

The prototype's evidence that matching works end to end. Pick 10 identifiable
CMU faculty within the corpus departments (see the ingestion bound in the
README conventions), write one query each that should surface that person,
and run every query against the service.

**Pass criterion:** the expected researcher is ranked in the top 5 for their
query.

To avoid tuning the test to pass, queries are written by a teammate other
than the corpus builder.

## Results

| Query | Expected researcher | Actual rank | Pass/fail |
| ----- | ------------------- | ----------- | --------- |
| I'm interested in why chatbots can be tricked into ignoring their safety rules, and how to make models harder to break. | Zico Kolter (MLD) | | |
| I want to train models across hospitals or phones without the data ever leaving where it lives. | Virginia Smith (MLD) | | |
| I'd like to study how conference paper reviewing goes wrong — biased scores, collusion, bad reviewer assignments — and build tools to fix it. | Nihar B. Shah (MLD) | | |
| I care about making translation and language tools work for languages that barely have any training data. | Graham Neubig (LTI) | | |
| I want to understand how chat systems pick up stereotypes and offensive language, and whether they can handle social situations appropriately. | Maarten Sap (LTI) | | |
| I'm curious how much electricity and carbon it takes to train and run big AI models, and how to make them more efficient. | Emma Strubell (LTI) | | |
| I want to build AI that writes code alongside a programmer and figures out what someone actually means when their instructions are vague. | Daniel Fried (LTI) | | |
| I'm excited about robots that can follow spoken instructions and connect words to what they see and do in the physical world. | Yonatan Bisk (LTI) | | |
| I want to build technology that helps blind and disabled people use their phones and computers. | Jeffrey Bigham (HCII) | | |
| I'm interested in how social workers and teachers actually use algorithmic tools on the job, and how to design AI that supports their judgment instead of replacing it. | Kenneth Holstein (HCII) | | |

## Notes for execution

- Rows 4 and 7 carry the highest cross-surfacing risk. Neubig also publishes
  on code generation and agents, so row 7's emphasis stays on pragmatics and
  understanding vague intent. A Neubig #2 on row 7 is worth noting, but the
  expected #1 stands.
- Bigham (HCII/LTI) and Bisk (LTI/Robotics) hold joint appointments. Confirm
  the ingest captured them under the expected department before treating a
  miss as a retrieval failure.
- Several researchers split time with industry (Kolter, Bigham, Sap), which
  can fragment OpenAlex affiliation records. Spot-check that their 2021+
  papers resolve to CMU in the data before treating a miss as a retrieval
  failure.
